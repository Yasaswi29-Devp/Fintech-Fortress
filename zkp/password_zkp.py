import hashlib
import random

class PasswordZKP:
    def __init__(self):
        # Large prime for security
        self.p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
        self.g = 2  # Generator
        
    def generate_keypair(self, password: str):
        """Generate public-private keypair from password"""
        private_key = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        public_key = pow(self.g, private_key, self.p)
        return private_key, public_key
    
    def generate_proof(self, password: str):
        """Generate ZKP proof for password"""
        # Generate private key from password
        private_key = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        # Calculate public key
        public_key = pow(self.g, private_key, self.p)
        
        # Generate random number for proof
        r = random.randint(1, self.p-1)
        # Calculate commitment
        commitment = pow(self.g, r, self.p)
        
        # Generate challenge
        challenge = int(hashlib.sha256(str(commitment).encode()).hexdigest(), 16)
        # Calculate response
        response = (r + challenge * private_key) % (self.p-1)
        
        return {
            'public_key': public_key,
            'commitment': commitment,
            'challenge': challenge,
            'response': response
        }
    
    def verify_proof(self, proof, stored_public_key):
        """Verify ZKP proof"""
        try:
            commitment = proof['commitment']
            challenge = proof['challenge']
            response = proof['response']
            
            # Verify the proof
            left_side = pow(self.g, response, self.p)
            right_side = (commitment * pow(stored_public_key, challenge, self.p)) % self.p
            
            return left_side == right_side
        except Exception as e:
            print(f"Verification error: {e}")
            return False
