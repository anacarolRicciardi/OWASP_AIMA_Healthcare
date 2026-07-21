# Markdown Heading Rules

This project is designed for asynchronous collaboration and final PDF generation.  
The content is structured as chapters and sections in Markdown. Please follow these guidelines to ensure consistency.

# Folder and File Structure

Each top-level folder represents a major chapter (e.g., `Introduction`, `The Model`, `Appendix`).
Inside the Model Directory, the actual AIMA Model is describe with a repetitive folder/file structure 
to represent chapters and so on. 

- `00_index.md` → Defines the chapter title (starts with `##`)
- Numbered `.md` files → Each file is a section (starts with `###`)
- Optional: assets (images, diagrams) stored in `/assets/` or relative paths

**Example:**
```
10_The_Model/
├── 10_Governance/                             // Represents the Governance Pillar
│   ├── 00_index.md                            // Describes the Governance Pillar (starts with ##)
│   ├── 10_Strategy_And_Metrics.md             // Strategy & Metrics practice (starts with ###)
│   ├── 20_Policies_And_Procedures.md          // Policies & Procedures practice (starts with ###)
│   └── 30_Education_And_Awareness.md          // Education & Awareness practice (starts with ###)
└── assets/                                    // Diagrams, images, etc.
```

## Heading Levels

| Purpose                | Heading Level |
|------------------------|----------------|
| Chapter Title          | `##`           |
| Section Title          | `###`          |
| Subsection Title       | `####`         |
| Nested Subsection      | `#####`        |

## Writing Guidelines

- Each `.md` file must begin with the appropriate heading level based on its placement in the folder hierarchy.
- Use consistent and semantic header levels: do not skip levels (e.g., from `###` directly to `#####`).

## Assets

- Store diagrams and images in the `assets/` folder within the chapter directory.
- Use relative paths when referencing assets (e.g., `![Diagram](./assets/example.png)`).

## File Naming

- Use a two-digit numeric prefix for ordering (e.g., `10_Governance.md`, `20_Data_Management.md`)
- Use snake_case for file names with multiple words.

## Consistency

- Ensure each file begins with the correct heading level.
- Keep a clean hierarchy that aligns with the folder and filename structure.
- When in doubt, match the heading level to the file’s role in the outline structure: folder (chapter) → `##`, file (section) → `###`, subsection → `####`, etc.
