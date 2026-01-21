# Production Journal: Code-as-Video 🎬

This journal documents the evolution of MiniStudio's "Stateful Filmmaking" engine. It maps the Python scripts (The Code) to their visual results (The Video) and candidly discusses the current technical challenges on the path to high-fidelity AI cinematography.

---

## 📽️ Demo 1: The ContextBytes Brand Story
**Goal**: Create a 1-minute emotional journey with consistent 'Ghibli Heroine' (Emma) and 'Intellectual' (David) characters.

| The Python Script | The Complete Production |
| :--- | :--- |
| <details><summary>View Script</summary>```python
# EMMA Identity Grounding
EMMA = Character(
    identity={"hair": "chestnut brown bob", "eyes": "amber"}
)
# Scene 4: The Bloom
ShotConfig(
    environment=GHIBLI_ATELIER,
    action="Glowing vines of data grow around the desk."
)
```</details> | **[▶ Watch Full Ghibli 2.0 Story](contextbytes_production/contextbytes_brand_story.mp4)**<br>*(6 Shots • 48s • 4K Shinkai Style)* |

### ⚠️ Challenges Noted:
- **Visual Drift**: Despite identity grounding, Emma's blue sweater occasionally changes shade between Shot 1 and Shot 6.
- **Environment Flickering**: The mahogany bookshelves in the `GHIBLI_ATELIER` shifted slightly in layout between the Medium Shot and Wide Shot.

---

## 🧬 Demo 2: The Last Algorithm (Complex Story)
**Goal**: Multi-character interaction across a scene change (Night Lab → Dawn Lab).

| The Python Script | The Complete Production |
| :--- | :--- |
| <details><summary>View Script</summary>```python
# Sarah: focused → shocked → fearful
SARAH.current_state={"expression": "fearful"}
# ARIA (AI Hologram)
ARIA = Character(identity={"form": "liquid light hologram"})
```</details> | **[▶ Watch Full Complex Story](the_last_algorithm/the_last_algorithm.mp4)**<br>*(8 Shots • 64s • Cinematic Night/Dawn Lab)* |

### ⚠️ Challenges Noted:
- **Temporal Stability**: Sarah's movements during her emotional transition were slightly "jittery" between keys.
- **Audio Sync**: In Shot 3, the Google TTS audio finished 0.5s before the video ended, requiring a manual fix in `utils.py`.

---

## 🛠️ The Path Forward: AI Filmmaking 2.0

We have identified that **frame-level statefulness** is the next frontier. We are currently analyzing course material to implement:
1.  **Consistent Background Masks**: Forcing the AI to "paint" characters on top of a locked, unchanging environment frame.
2.  **Audio-Driven Animation**: Using the TTS waveform to drive character mouth movement and facial intensity.
3.  **Universal Seeds**: Implementing deterministic noise across all shots in a scene to eliminate color-grading drift.

### 🌟 Handover Note
The mantle now passes to the developer. These challenges are not bugs, but the current **technological ceiling** of generative video. By following this journal, we can systematically break through them using advanced cinematography techniques.
