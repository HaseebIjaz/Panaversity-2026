# Lec 6 Task - My Portfolio

This is a simple one-page personal portfolio website created using the Markdown → HTML workflow.

# Deployment Link

This site is deplyed on Github Pages at : [https://haseebijaz.github.io/Panaversity-2026/](https://haseebijaz.github.io/Panaversity-2026/)

## Deplyment Steps

1. Create an orphan gh-pages branch:

```bash
git checkout --orphan gh-pages
```

2.Remove all existing files from the branch:

```bash
git rm -rf .
```

3. Add your website files, making sure the homepage is named:

```
index.html
```

4. In GitHub, go to Settings → Pages.
   Select:

```
Source: Deploy from a branch
Branch: gh-pages
Folder: / (root)
```

Click Save. GitHub Pages will automatically publish the index.html file from the orphan gh-pages branch.

## Files & Folders

- `index.html` — Portfolio website
- `portfolio.md` — Portfolio Data
- `prompt.md` — Prompts
- `iterated_versions` — Iterations [HTML]

## Technologies

- Google AI Studio

## Author

Haseeb Ijaz

## Final Version Preview

![portfolio_image](images/Portfolio.PNG)
