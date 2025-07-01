def generate_color(class_id, alpha=255):
    """
    Generate a unique RGB color for a given class ID using bit manipulation.
    
    Args:
        class_id (int): The class identifier (0-based)
        alpha (int): Alpha channel value (0-255), default 255
    
    Returns:
        tuple: (r, g, b, a) color values as integers (0-255)
    """
    # Skip the first color (black) by adding 1
    class_id += 1
    
    # Initialize RGB values
    r = g = b = 0
    c = class_id
    
    # Process 8 bits to generate color values
    for j in range(8):
        # Extract bits and distribute across RGB channels
        r |= ((c & 1) << (7 - j))        # bit 0 -> red channel
        g |= (((c >> 1) & 1) << (7 - j)) # bit 1 -> green channel  
        b |= (((c >> 2) & 1) << (7 - j)) # bit 2 -> blue channel
        
        # Shift to next group of 3 bits
        c >>= 3
    
    return (r, g, b, alpha)


def generate_color_normalized(class_id, alpha=1.0):
    """
    Generate a unique RGB color for a given class ID with normalized values (0-1).
    
    Args:
        class_id (int): The class identifier (0-based)
        alpha (float): Alpha channel value (0-1), default 1.0
    
    Returns:
        tuple: (r, g, b, a) color values as floats (0.0-1.0)
    """
    r, g, b, a = generate_color(class_id, int(alpha * 255))
    return (r / 255.0, g / 255.0, b / 255.0, alpha)


# Example usage and test function
def test_color_generation():
    """Test the color generation function with some examples."""
    print("Class ID -> RGB Color")
    print("-" * 25)
    
    for i in range(10):
        r, g, b, a = generate_color(i)
        print(f"{i:8d} -> ({r:3d}, {g:3d}, {b:3d})")
    
    print("\nNormalized colors (0-1):")
    print("-" * 25)
    
    for i in range(5):
        r, g, b, a = generate_color_normalized(i)
        print(f"{i:8d} -> ({r:.3f}, {g:.3f}, {b:.3f})")


# Additional utility function to convert to hex
def generate_color_hex(class_id):
    """
    Generate a unique hex color for a given class ID.
    
    Args:
        class_id (int): The class identifier (0-based)
    
    Returns:
        str: Hex color string (e.g., "#FF0000")
    """
    r, g, b, _ = generate_color(class_id)
    return f"#{r:02X}{g:02X}{b:02X}"


if __name__ == "__main__":
    # Run tests
    test_color_generation()
    
    print("\nHex colors:")
    print("-" * 15)
    for i in range(5):
        hex_color = generate_color_hex(i)
        print(f"Class {i}: {hex_color}")