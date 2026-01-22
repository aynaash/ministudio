# Story Comparison: Simple vs Complex

## Simple Story: Quantum Mechanics TikTok

**Complexity Level**: 

### Features
-  2 characters (Grandfather, Granddaughter)
-  1 static environment (Cozy Study)
-  7 shots, all in same location
-  Character voices
-  Basic continuity

### Use Case
Educational content, tutorials, simple narratives

### Code
```python
scene = SceneConfig(
    characters={"Grandfather": GRANDFATHER, "Granddaughter": GRANDDAUGHTER},
    environment=COZY_STUDY,  # Never changes
    shots=[...]  # All shots in same place
)
```

---

## Complex Story: The Last Algorithm

**Complexity Level**: 

### Features
-  2 characters (Dr. Sarah, ARIA hologram)
-  **Emotional evolution** (focused  shocked  fearful  accepting)
-  **2 dynamic environments** (Night Lab  Dawn Lab)
-  **Scene transitions** with character preservation
-  **Multi-character interactions** with distinct personalities
-  **Cinematic lighting changes** (cold blue  warm golden)
-  Advanced continuity across environment changes

### Use Case
Dramatic stories, sci-fi narratives, complex character arcs

### Code
```python
# Scene 1: Night
scene1 = SceneConfig(
    environment=TECH_LAB_NIGHT,
    characters={"Dr. Sarah": DR_SARAH, "ARIA": ARIA_AI}
)

# Scene 2: Dawn (ENVIRONMENT CHANGES, CHARACTERS PERSIST)
scene2 = SceneConfig(
    environment=LAB_DAWN,  # Different lighting!
    characters={"Dr. Sarah": DR_SARAH, "ARIA": ARIA_AI}  # Same characters!
)
```

---

## What Makes It Complex?

### 1. Character Emotional Evolution
```
Simple: Grandfather stays "enthusiastic" throughout
Complex: Sarah evolves focused  shocked  fearful  accepting
```

### 2. Dynamic Backgrounds
```
Simple: Cozy Study (static)
Complex: Night Lab  Dawn Lab (dynamic lighting transition)
```

### 3. Continuity Challenge
```
Simple: Same environment = easy continuity
Complex: Different environment = must preserve characters while changing background
```

### 4. Character Types
```
Simple: Two humans
Complex: Human + AI hologram (different visual properties)
```

---

## Test Both!

### Simple Story
```bash
doppler run -- python examples/quantum_tiktok_demo.py --sample
```

### Complex Story
```bash
doppler run -- python examples/complex_story_demo.py --sample
```

Both demonstrate the same state machine, just different complexity levels!
