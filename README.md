# Ryan Cartwright: CS 499 ePortfolio

My CS 499 Computer Science Capstone ePortfolio at Southern New Hampshire University, published with GitHub Pages.

- **Home:** my professional self-assessment, followed by my skills.
- **About:** my background and path into computer science.
- **Projects:** TrakCode, the capstone artifact, plus other projects. The TrakCode page links the code review video, the original artifact, and a page for each of the three enhancements with its narrative and before-and-after code.

The capstone source code is in [CountryCoder44/trakcode-cs499](https://github.com/CountryCoder44/trakcode-cs499).

## How the site is built

Plain HTML, CSS, and a few lines of JavaScript, with no framework. The narratives are written in Markdown in `content/`, and `build.py` (Python standard library only) renders them and the other pages into the HTML files at the root, which GitHub Pages serves as-is.

```bash
python build.py
```
