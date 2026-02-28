# PDCA AI Coding Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/YiK1991/Skill/tree/main/pdca)
[![Claude AI](https://img.shields.io/badge/Claude-AI%20Skill-purple.svg)](https://claude.ai)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> Production-ready Claude Skill implementing the Plan-Do-Check-Act framework for AI-assisted code generation.

Based on [Ken Judy's InfoQ article](https://www.infoq.com/articles/PDCA-AI-code-generation/) - a research-backed methodology that reduces debugging time by 80% while maintaining code quality.

---

## ⚡ Quick Links

📖 [Getting Started Guide](docs/GETTING-STARTED.md) | 🤝 [Contributing](CONTRIBUTING.md) | 📝 [Changelog](CHANGELOG.md) | 🔒 [Security](SECURITY.md)

---

## 🎯 What is This?

This skill helps you write better code with AI assistants (Claude Code, Cline, etc.) by providing:
- ✅ Structured workflow preventing common AI coding pitfalls
- ✅ Test-driven development discipline
- ✅ Quality metrics tracking
- ✅ Continuous improvement through retrospectives
- ✅ Prevention of code duplication and regressions

## 📊 Research-Backed Results

From the InfoQ article's experiment:
- 10% fewer tokens used
- 34% less production code (more maintainable)
- 30% more test coverage
- 80% less troubleshooting time
- Better developer experience

## 🚀 Quick Start

### Installation (< 2 minutes)

**Option 1: Download Release**
1. Go to [Releases](https://github.com/YiK1991/Skill/releases/latest)
2. Download the latest release
3. Upload to Claude.ai:
   - Open [Claude.ai](https://claude.ai)
   - Click **Skills** menu
   - Select **"Upload Skill"**
   - Choose `SKILL.md`
4. ✅ Ready to use!

**Option 2: Build from Source**
```bash
git clone https://github.com/YiK1991/Skill.git
cd pdca-ai-coding-skill
# Upload SKILL.md to Claude.ai
```

### Your First Session (< 5 minutes)

```
I need to implement [your feature]. Let's use the PDCA framework.
```

Claude will guide you through:
1. **Analysis** - Search existing patterns, propose approaches
2. **Planning** - Break into TDD steps
3. **Implementation** - Red-Green-Refactor with human oversight
4. **Check** - Verify quality and completeness
5. **Retrospective** - Learn and improve

## 📁 Repository Structure

```
.
├── SKILL.md                      # Main skill file — upload to Claude.ai
├── references/                   # Prompt templates
│   ├── working-agreements.md
│   ├── analysis-prompt.md
│   ├── planning-prompt.md
│   ├── implementation-prompt.md
│   ├── completion-prompt.md
│   └── retrospective-prompt.md
├── scripts/                      # Automation tools
│   ├── track_metrics.py         # Quality metrics tracking
│   └── init_session.py          # Session initialization
├── assets/
│   └── session-template.md      # Session logging template
└── docs/                        # Additional documentation
    ├── README.md
    ├── GETTING-STARTED.md
    ├── PROJECT-CONFIGURATION.md
    └── REFINEMENTS-V1.1.md
```

## 🎓 Documentation

- **[GETTING-STARTED.md](docs/GETTING-STARTED.md)** - Your 5-minute quick start guide
- **[PROJECT-CONFIGURATION.md](docs/PROJECT-CONFIGURATION.md)** - Guide for project-specific setup
- **[README.md](README.md)** - Complete package overview
- **[REFINEMENTS-V1.1.md](docs/REFINEMENTS-V1.1.md)** - Technical refinements and validation

## 🔧 Key Features

### Working Agreements
- Test-driven development discipline
- Small, atomic commits (<100 lines, <5 files)
- Respect for existing architecture
- Human accountability for all AI-generated code

### 5-Phase Workflow
1. **Plan (Analysis)** - 2-10 min: Search patterns, propose approaches
2. **Plan (Breakdown)** - 2 min: Create TDD execution plan
3. **Do** - <3 hours: Implement with red-green-refactor
4. **Check** - 5 min: Verify quality and process adherence
5. **Act** - 2-10 min: Retrospective and continuous improvement

### Quality Metrics
Track your progress:
- Large commits: <20% (>100 lines)
- Sprawling commits: <10% (>5 files)
- Test-first discipline: >50%
- Avg files per commit: <5
- Avg lines per commit: <100

### Automation Scripts
```bash
# Track quality metrics
python scripts/track_metrics.py --repo /path/to/repo --since "7 days ago"

# Initialize session with logging
python scripts/init_session.py "Feature name" --objective "What you're building"
```

## 🎯 Use Cases

### ✅ Use This For:
- Implementing new features (1-3 hour tasks)
- Refactoring existing code
- Adding integrations
- Any task requiring quality and maintainability

### ❌ Don't Use For:
- Quick prototypes or experiments
- Trivial changes
- Simple bug fixes (use Lite or Lightweight mode)

## 💡 Why This Works

From the article's research:

**The Problem:**
- AI code generation increases output but decreases delivery stability
- 10x increase in duplicated code
- Quality issues and integration problems

**The Solution:**
- Structured prompting outperforms ad-hoc by 1-74%
- PDCA reduces software defects by 61%
- Human-in-the-loop with clear intervention points

## 📈 Expected Results

**After 1 Week:**
- Comfortable with workflow
- Catching AI errors early
- Smaller, better commits

**After 1 Month:**
- Metrics trending positive
- Fewer regressions
- Faster code reviews
- Less debugging time

**After 3 Months:**
- Significantly better code quality
- Faster delivery
- Team wants to adopt it

## 🛠️ Customization

### Project-Specific Configuration

The PDCA skill works globally across all projects. For project-specific tech stack and conventions, you can optionally create a `.claude/instructions.md` file in your project root. This tells Claude about your specific tech choices without modifying the skill itself.

**See [docs/PROJECT-CONFIGURATION.md](docs/PROJECT-CONFIGURATION.md) for complete guide on when and how to use project-specific configuration.**

### Customizing the Skill Itself

The skill is designed to be customized:

```bash
# Clone and customize
git clone https://github.com/YiK1991/Skill.git
cd pdca-ai-coding-skill

# Edit prompts in references/
# Update working agreements
# Adjust quality targets
```

## ❓ FAQ

<details>
<summary><b>Does this work with Claude Code and Cline?</b></summary>

Yes! The skill works with any Claude-based coding assistant including Claude Code, Cline, and the Claude.ai web interface.
</details>

<details>
<summary><b>How long does a PDCA session take?</b></summary>

Typical sessions are 1-3 hours. The framework helps you break larger tasks into these manageable chunks. You can also use the lightweight version for 15-30 minute tasks.
</details>

<details>
<summary><b>Can I customize the prompts?</b></summary>

Absolutely! The prompts are designed as starting points. Extract the skill, modify the references/ files, and repackage. The retrospective process will help you refine them based on your needs.
</details>

<details>
<summary><b>Do I need to follow all 5 phases every time?</b></summary>

For best results, yes. However, the skill includes lightweight versions for simple tasks. At minimum, always do TDD implementation and retrospectives.
</details>

<details>
<summary><b>What if my team doesn't use TDD?</b></summary>

The framework still provides value through analysis, planning, and retrospectives. However, TDD is core to preventing AI-generated regressions. Consider adopting TDD at least for AI-assisted coding.
</details>

<details>
<summary><b>How do I track metrics without GitHub Actions?</b></summary>

Use the included `track_metrics.py` script locally:
```bash
python scripts/track_metrics.py --repo . --since "7 days ago"
```
</details>

<details>
<summary><b>Do I need a .claude/instructions.md for every project?</b></summary>

No! Only create it for projects with specific conventions or when you find yourself repeating the same context. See [PROJECT-CONFIGURATION.md](docs/PROJECT-CONFIGURATION.md) for guidance.
</details>

## 🌟 Star History

If you find this useful, please star the repository! It helps others discover the framework.

[![Star History Chart](https://api.star-history.com/svg?repos=YiK1991/Skill&type=Date)](https://star-history.com/#YiK1991/Skill&Date)

## 💬 Community

- **Discussions**: [GitHub Discussions](https://github.com/YiK1991/Skill/discussions) - Share experiences, ask questions
- **Issues**: [Bug reports and feature requests](https://github.com/YiK1991/Skill/issues)
- **Twitter**: Share your results with `#PDCACoding`

## 📚 Learn More

- [Original InfoQ Article](https://www.infoq.com/articles/PDCA-AI-code-generation/)
- [Author's GitHub](https://github.com/kenjudy/pdca-code-generation-process/)
- [Code Quality Metrics](https://github.com/kenjudy/code-quality-metrics/)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick ways to contribute:**

1. **⭐ Star the repo** - Help others discover it
2. **🐛 Report bugs** - Use our [issue templates](.github/ISSUE_TEMPLATE/)
3. **💡 Suggest improvements** - Based on your retrospectives
4. **📝 Improve docs** - Fix typos, add examples
5. **🔧 Submit PRs** - Share your prompt refinements

**Areas we need help:**
- Framework-specific adaptations (React, Django, etc.)
- Language-specific variations (Python, TypeScript, Go, etc.)
- Real-world case studies
- Video tutorials
- Translations

See our [roadmap in CHANGELOG.md](CHANGELOG.md#future-roadmap) for planned features.

## 📄 License

MIT License - feel free to adapt for your needs

## 🙏 Credits

- **Framework:** Ken Judy's PDCA methodology from [InfoQ article](https://www.infoq.com/articles/PDCA-AI-code-generation/)
- **Implementation:** Skill created by Claude (Anthropic) based on the article
- **Validation:** Multiple iterations with article cross-referencing

## 🔗 Related Resources

- [Anthropic Claude](https://www.anthropic.com/claude)
- [Claude Skills Documentation](https://docs.anthropic.com/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [PDCA Cycle](https://en.wikipedia.org/wiki/PDCA)

## 📞 Support

Issues? Ideas? Open an issue or discussion in this repository.

Want to share your experience? We'd love to hear how PDCA is working for you!

---

**Version:** 1.1  
**Last Updated:** 2026-02  
**Status:** Production Ready ✅
