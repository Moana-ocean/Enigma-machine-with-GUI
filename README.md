# Enigma Machine Simulator

A Python implementation of the Enigma machine cipher with a graphical user interface.

## Features

- Simulates the Enigma machine encryption/decryption
- GUI interface for easy operation
- Configurable rotors (I-VI)
- Plugboard support (up to 10 pairs)
- History log with restore functionality
- Real-time encryption/decryption

## Files

- `Enigma.py` - Core Enigma machine implementation
- `enigma_gui_simple.py` - GUI application

## Usage

Run the GUI application:

```bash
python enigma_gui_simple.py
```

Or use the core module directly:

```python
from Enigma import Rotor, Reflector, Plugboard, Enigma_machine, ROTORS, REFLECTOR

# Create rotors
rotor1 = Rotor(ROTORS["I"], None, position='E')
rotor2 = Rotor(ROTORS["II"], None, position='A')
rotor3 = Rotor(ROTORS["VI"], None, position='J')

# Create machine
rotors = [rotor1, rotor2, rotor3]
reflector = Reflector(REFLECTOR)
plugboard = Plugboard([])
enigma = Enigma_machine(rotors, reflector, plugboard)

# Encrypt
ciphertext = enigma.encrypt("OCEAN")
print(ciphertext)
```

## Requirements

- Python 3.x
- tkinter (usually included with Python)

