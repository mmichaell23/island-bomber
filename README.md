# Island Bomber Game

A top-down action game where you navigate a large island and throw bombs with different abilities to defeat enemies that can also throw bombs back at you.

![Image](https://github.com/user-attachments/assets/348ca735-c83a-4a56-9090-9d293a314ec9)

## Game Features

### Core Gameplay
- Top-down perspective gameplay with 3D-like effects
- Large island environment with trees, palm trees, rocks, and water spots
- Physics-based movement with acceleration and deceleration
- Jumping mechanics with gravity and bouncing effects
- Fullscreen support (toggle with F key)

### Combat System
- Three bomb types with unique abilities:
  - **Regular Bomb**: Standard explosion with contact detonation
  - **Timer Bomb**: Larger explosion with 1.5-second timer (high damage)
  - **Cracking Bomb**: Splits into multiple fragments that explode separately
- Hold-and-release mechanic for timer bombs (cook bombs before throwing)
- Limited bomb ammo with automatic reload system (3 bombs max, 2-second reload)
- Realistic bomb physics with bouncing, rotation, and 3D effects
- Particle-based explosions with dynamic lighting effects

### Enemy AI
- Aggressive enemies that actively chase and attack the player
- Enemies can throw bombs at the player (regular, cracking, and timer bombs)
- Different AI states: patrol, chase, attack, throw_bomb
- Visual indicators when enemies are about to throw bombs
- Enemies have health bars and take damage from explosions

### Power-Up System
- Four types of power-ups that spawn randomly:
  - **Health Power-Up**: Heals the player for 50 health points
  - **Speed Power-Up**: Increases player movement speed by 50% for 5 seconds
  - **Damage Power-Up**: Increases bomb damage by 50% for 5 seconds
  - **Shield Power-Up**: Adds a shield that absorbs up to 50 damage points
- Power-ups have visual effects and animations
- Power-ups can spawn randomly or when defeating enemies

### Sound System
- Integrated sound manager with volume control
- Sound effects for:
  - Throwing bombs
  - Explosions
  - Collecting power-ups
  - Taking damage
  - Game over
- Volume control with + and - keys
- Mute toggle with M key

### Visual Effects
- Dynamic shadows that change with height
- Particle effects for explosions and power-ups
- Visual feedback for damage, shields, and speed boosts
- Bobbing animations for characters and objects
- Eye tracking for characters (eyes follow targets)
- Motion blur for fast-moving bombs

### Game Recording Feature
- Built-in video recording functionality
- Record button in the game interface (bottom right corner)
- Saves gameplay as MP4 videos in the "records" folder
- Shows recording status and duration while recording
- Automatic timestamp naming for recordings
- Optimized for performance with frame skipping and threading
- Memory usage indicator during recording

### Game Systems
- Score tracking and difficulty progression
- Health system with visual feedback
- Shield system for damage absorption
- Bomb ammo system with visual reload indicator
- Game over and restart functionality
- HUD with game information and status indicators
- FPS display toggle (F3 key)

## Controls

- **WASD**: Move the player
- **Mouse**: Aim
- **Left Click (Hold)**: Hold timer bomb, release to throw
- **Left Click**: Throw bomb or interact with UI elements
- **Spacebar**: Jump
- **1-3 Keys**: Switch between bomb types
  - 1: Timer Bomb (high damage)
  - 2: Cracking Bomb (multiple hits)
  - 3: Regular Bomb (contact explosion)
- **F**: Toggle fullscreen mode
- **F3**: Toggle FPS display
- **M**: Toggle sound mute
- **+/-**: Increase/decrease volume
- **R**: Restart game (when game over)

## Requirements

- Python 3.x
- Pygame library
- OpenCV library (for recording feature)
- NumPy library
- Threading support

## Installation

1. Make sure you have Python installed
2. Install required libraries:
   ```
   pip install pygame opencv-python numpy
   ```
3. Run the game:
   ```
   python main.py
   ```

## Game Structure

- `main.py`: Main game loop and initialization
- `scripts/player.py`: Player character implementation with 3D effects
- `scripts/bomb.py`: Different bomb types and behaviors with physics
- `scripts/island.py`: Detailed island environment generation
- `scripts/camera.py`: Camera system for top-down view
- `scripts/enemy.py`: Enemy AI and behaviors with attack functionality
- `scripts/powerup.py`: Power-up system implementation
- `scripts/recorder.py`: Game recording functionality with optimization
- `scripts/sound_manager.py`: Sound system with volume control
- `assets/`: Sound effects files
- `records/`: Saved game recordings

## Tips for Playing

- Use Timer Bombs for maximum damage against tough enemies
- Hold timer bombs to "cook" them before throwing for precise timing
- Cracking Bombs are effective against groups of enemies
- Regular Bombs are good for quick attacks as they explode on contact
- Manage your bomb ammo carefully - you only have 3 bombs at a time
- Collect power-ups to gain advantages in combat
- Watch out for enemies with bombs - they can deal significant damage
- Use the shield power-up when facing multiple bomber enemies
- Jump to avoid enemy bombs and attacks
- Record your best gameplay moments with the recording feature
- Switch to fullscreen mode for a more immersive experience
