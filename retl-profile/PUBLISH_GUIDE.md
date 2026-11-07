# Publishing your RETL profile README

GitHub shows a profile README only from a **public repository named exactly like your username**.

## 1. Create the profile repository
1. Go to https://github.com/new
2. Repository name: `rheillunio2-byte` (must match your username exactly)
3. Set it to **Public** and tick **Add a README file** (GitHub shows a "special" notice).
4. Click **Create repository**.

## 2. Upload the files
Upload these into the repository root, keeping the folder structure:

```
rheillunio2-byte/
├── README.md
├── assets/
│   ├── hero-animation.gif      (animated hero)
│   ├── hero-fallback.png       (static hero, 2400x800)
│   ├── typing.svg  divider.svg  focus-network.svg  stack.svg
│   ├── research-markov.svg  promptpilot-flow.svg  achievements.svg  footer.svg
│   ├── logo-horizontal.png  logo-mark.png        (transparent versions of your logos)
│   └── me-portrait.png  me-avatar.png            (your photo crops)
└── source/            (optional, but good to keep)
    ├── render_hero.py  build_gif.sh  make_svgs.py  prep_images.py
```

**Web:** open the repo → **Add file → Upload files** → drag the contents of this folder in → **Commit changes**. Replace the existing README.md when asked.

**Git:**
```bash
git clone https://github.com/rheillunio2-byte/rheillunio2-byte.git
cd rheillunio2-byte
# copy README.md, assets/ and source/ in, then:
git add .
git commit -m "Add profile README with animated hero"
git push
```

## 3. Fill in the TODO markers
Search README.md for `TODO` and replace each with the real value:
- Repository links for SmartFileOrganizerPro, CommitQuest, DayForm and the blood pressure web app
- Your academic distinctions, with issuer and year
- Add your certificates' exact details if you want them listed
- The "Google I/O Extended" card and the achievements graphic are text inside `source/make_svgs.py` (function `achievements`), so edit them there and re-run it

## 4. Check it
Open https://github.com/rheillunio2-byte. The GIF should loop and the stats images should load. The stats cards come from public third-party services; if one is slow or rate-limited, it usually loads on a refresh a few minutes later. For better reliability, deploy your own copy of github-readme-stats.

## Editing the animation
`source/render_hero.py` is a Pillow + NumPy script. Install Pillow and numpy, then:
```bash
python3 render_hero.py frames   # renders PNG frames to ./frames
sh build_gif.sh                 # needs ffmpeg; writes ../assets/hero-animation.gif
python3 render_hero.py still    # rewrites ../assets/hero-fallback.png (2400x800)
```
Text, colors and panel contents are near the top of the file and in `frame()`. If your fonts are elsewhere, edit the `INTER` and `MONO` paths.

## The animated SVGs
The SVG graphics animate on GitHub when used with `<img src="assets/name.svg">`, as the README does. They are plain text files, so you can edit text and colors in `source/make_svgs.py` and run `python3 make_svgs.py`. They need no external fonts or images.

## Using the fallback image
If you ever want a static banner (for example a GIF load issue), replace the `<img src="assets/hero-animation.gif" ...>` line in README.md with `assets/hero-fallback.png`.
