ROTORS = {
    "I"   : "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II"  : "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III" : "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV"  : "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V"   : "VZBRGITYUPSDNHLXAWMJQOFECK",
    "VI"  : "JPGVOUMFYQBENHZRDKASXLICTW"
}

REFLECTOR = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

class Rotor:
    def __init__(self, wiring, notch, position='A') -> None:
        self.wiring = wiring
        # Notch is no longer used
        # Store position as integer (0-25)
        if isinstance(position, str):
            self.position = ord(position.upper()) - ord('A')
        else:
            self.position = position

    def get_position_letter(self) -> str:
        """Return the current position as a letter."""
        return chr(self.position + ord('A'))

    def set_position(self, pos) -> None:
        """Set the rotor position using a letter or integer."""
        if isinstance(pos, str):
            self.position = ord(pos.upper()) - ord('A')
        else:
            self.position = pos % 26

    def step(self) -> None:
        """Advance the rotor position by one, with wrap-around."""
        self.position = (self.position + 1) % 26

    def encode_forward(self, c: str) -> str:
        idx = (ord(c) - ord('A') + self.position) % 26
        wired_letter = self.wiring[idx]
        out_idx = (ord(wired_letter) - ord('A') - self.position) % 26
        return chr(out_idx + ord('A'))

    def encode_backward(self, c: str) -> str:
        idx = (ord(c) - ord('A') + self.position) % 26
        wired_idx = self.wiring.index(chr(idx + ord('A')))
        out_idx = (wired_idx - self.position) % 26
        return chr(out_idx + ord('A'))

class Reflector:
    def __init__(self, wiring: str) -> None:
        self.wiring = wiring

    def reflect(self, c: str) -> str:
        idx = ord(c) - ord('A')
        return self.wiring[idx]

class Plugboard:
    def __init__(self, pairs=None):
        self.mapping = {}
        if pairs:
            for a, b in pairs:
                if a == b or a in self.mapping or b in self.mapping:
                    raise ValueError(f"Invalid plugboard pair: {a}-{b}")
                self.mapping[a] = b
                self.mapping[b] = a

    def swap(self, c: str) -> str:
        return self.mapping.get(c, c)

class Enigma_machine:
    def __init__(self, rotors, reflector, plugboard=None) -> None:
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard if plugboard else Plugboard()
    
    def step_rotors(self):
        # Step rightmost rotor
        self.rotors[2].step()
        # If rightmost rotor completes a full cycle, step middle rotor
        if self.rotors[2].position == 0:
            self.rotors[1].step()
            # If middle rotor completes a full cycle, step leftmost rotor
            if self.rotors[1].position == 0:
                self.rotors[0].step()

    def encrypt_char(self, c):
        c = self.plugboard.swap(c)
        for rotor in reversed(self.rotors):
            c = rotor.encode_forward(c)
        c = self.reflector.reflect(c)
        for rotor in self.rotors:
            c = rotor.encode_backward(c)
        c = self.plugboard.swap(c)
        self.step_rotors()  # Step after encryption, not before
        return c

    def encrypt(self, text):
        text = text.upper().replace(" ", "")
        return ''.join(self.encrypt_char(c) for c in text if c.isalpha())


rotor1 = Rotor(ROTORS["I"], None, position='E')
rotor2 = Rotor(ROTORS["II"], None, position='A')
rotor3 = Rotor(ROTORS["VI"], None, position='J')
rotors = [rotor1, rotor2, rotor3]
reflector = Reflector(REFLECTOR)
plugboard = Plugboard([])

enigma = Enigma_machine(rotors, reflector, plugboard)
pt = "OCEAN"
ct = enigma.encrypt(pt)
print("PT:", pt)
print("CT:", ct)

# Reset rotors to initial positions
rotor1 = Rotor(ROTORS["I"], None, position='E')
rotor2 = Rotor(ROTORS["II"], None, position='A')
rotor3 = Rotor(ROTORS["VI"], None, position='J')
rotors = [rotor1, rotor2, rotor3]
enigma = Enigma_machine(rotors, reflector, plugboard)
decrypted = enigma.encrypt(ct)
print("Decrypted:", decrypted)