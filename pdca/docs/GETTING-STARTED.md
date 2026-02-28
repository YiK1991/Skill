# Getting Started with PDCA AI Coding

## 🎯 Your Mission: Better AI-Assisted Code

You're about to revolutionize how you work with AI coding assistants. This framework will help you:
- Write better, more maintainable code
- Reduce debugging time by 50%+
- Maintain architectural consistency
- Continuously improve your AI collaboration

---

## 📦 What You Have

Key pieces in this package:

| File | Purpose | When to Use |
|------|---------|-------------|
| **SKILL.md** | The skill file | Upload to Claude.ai immediately |
| **references/working-agreements.md** | Core principles cheat sheet | Print and keep at desk |
| **references/*.md** | Phase prompts | Loaded during PDCA phases |
| **docs/GETTING-STARTED.md** | This file! | Your quick start guide |
| **docs/REFINEMENTS-V1.1.md** | Deep-dive methodology | Reference when needed |

---

## ⚡ 5-Minute Quick Start

### Step 1: Upload the Skill (2 minutes)

1. Open [Claude.ai](https://claude.ai)
2. Look for **Skills** or **Tools** menu
3. Click **"Upload Skill"** or **"Add Skill"**
4. Upload `SKILL.md`
5. ✅ Done! The skill is now active

### Step 2: Your First Session (3 minutes setup)

Open a new chat with Claude and say:

```
I need to implement [YOUR FEATURE HERE]. 
Let's use the PDCA framework.
```

Example:
```
I need to implement user login with email/password. 
Let's use the PDCA framework.
```

Claude will:
1. Show you the working agreements
2. Ask for your business objective
3. Guide you through the workflow

### Step 3: Follow the Workflow

Just follow Claude's lead! It will walk you through:

1. **Analysis** - "What approach should we take?"
2. **Planning** - "Let's break this into TDD steps"
3. **Implementation** - "Step 1: Write failing test..."
4. **Check** - "Let's verify our work"
5. **Retrospective** - "What did we learn?"

**That's it!** You're using structured PDCA for AI coding.

---

## 🎓 Your First Week

### Day 1: Installation & First Session
- ✅ Upload skill to Claude.ai
- ✅ Do one simple feature (1-2 hours)
- ✅ Follow all 5 phases
- ✅ Read the retrospective carefully

### Day 2-3: Practice
- ✅ Do 2 more features
- ✅ Start intervening when AI goes off track
- ✅ Notice patterns in what works

### Day 4-5: Measure
- ✅ Run metrics on your commits
- ✅ See how you're doing vs targets
- ✅ Adjust based on retrospectives

---

## 📊 The 5-Phase Workflow (Visual)

```
┌─────────────────────────────────────────────────────────┐
│  PDCA CYCLE                                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  PLAN - Analysis (2-10 min)                        │
│     ├─ Search for existing patterns                    │
│     ├─ Propose 2-3 approaches                          │
│     └─ Recommend best approach                         │
│                                                         │
│  2️⃣  PLAN - Task Breakdown (2 min)                     │
│     ├─ Break into TDD steps                            │
│     ├─ Define acceptance criteria                      │
│     └─ Set checkpoints                                 │
│                                                         │
│  3️⃣  DO - Implementation (<3 hours)                    │
│     ├─ RED: Write failing test                         │
│     ├─ GREEN: Make test pass                           │
│     ├─ REFACTOR: Improve code                          │
│     └─ COMMIT: Save progress                           │
│                                                         │
│  4️⃣  CHECK - Completion (5 min)                        │
│     ├─ Verify all tests pass                           │
│     ├─ Check code quality                              │
│     └─ Confirm completeness                            │
│                                                         │
│  5️⃣  ACT - Retrospective (2-10 min)                    │
│     ├─ What worked well?                               │
│     ├─ What could be better?                           │
│     └─ One improvement for next time                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Optional: Project-Specific Configuration

The PDCA skill works great out-of-the-box, but for projects with specific tech stacks or team conventions, you can add a `.claude/instructions.md` file to your project root.

### When to Add Project Config

**Add `.claude/instructions.md` if:**
- ✅ Your project uses specific frameworks (Next.js vs Vite, TypeScript vs JavaScript)
- ✅ You have team conventions that differ from defaults
- ✅ You keep repeating the same context every session
- ✅ You work on complex enterprise projects

**Skip it if:**
- ❌ Simple personal projects
- ❌ Standard tech stack with common patterns
- ❌ Just prototyping or experimenting

### Quick Setup (2 minutes)

```bash
# In your project root
mkdir .claude
nano .claude/instructions.md
```

**Minimal template:**
```markdown
# Project: [Your Project Name]

## Tech Stack
- Framework: [e.g., Next.js 14]
- Language: [e.g., TypeScript]
- Database: [e.g., PostgreSQL + Prisma]

## Key Conventions
- [e.g., Use server components by default]
- [e.g., API routes in app/api/]
- [e.g., Functional components only]
```

**For detailed guide and templates, see [PROJECT-CONFIGURATION.md](PROJECT-CONFIGURATION.md)**

---

## 🎯 Key Success Factors

### ✅ DO These Things

1. **Read working agreements** before each session
2. **Let analysis run** - it prevents code duplication
3. **Intervene early** - stop AI when it goes wrong
4. **Commit frequently** - after each green test
5. **Do retrospectives** - this is where you improve

### ❌ DON'T Do These Things

1. **Skip analysis** - you'll duplicate code
2. **Skip tests** - you'll debug for hours
3. **Let AI ramble** - intervene when off track
4. **Make huge commits** - keep them small
5. **Skip retrospectives** - you won't improve

---

## 🛠️ Tools You Got

### Quality Metrics Script

Track your code quality:

```bash
# See how you're doing
python scripts/track_metrics.py --repo . --since "7 days ago"

# Output shows:
# ✅ Large commits: 15% (target: <20%)
# ✅ Sprawling commits: 8% (target: <10%)
# ✅ Test-first: 65% (target: >50%)
```

### Session Logger

Start structured sessions:

```bash
python scripts/init_session.py "Feature Name" \
  --objective "What you're building" \
  --time 2
```

Creates a log file to fill in as you work.

---

## 🎨 Complexity Modes

**Not all tasks are equal!** Use the right mode:

### ⚪ Lite (Trivial, No Behavior Change)
**When:** <50 lines, single file, reuse existing pattern, no interface change
**Skip:** All prompts — just TDD + commit
**Example:** "Fix typo in validation message"

### 🟢 Lightweight (Simple, Existing Patterns)
**When:** Small task with behavior change, clear existing examples
**Skip:** Detailed analysis
**Keep:** TDD + retrospective
**Example:** "Add new REST endpoint like existing ones"

### 🟡 Full (Complex, Novel Tasks)
**When:** New integrations, architectural changes, >50 lines
**Use:** All 5 phases fully
**Example:** "Integrate new payment provider"

### 🔴 Emergency (Production Bug Fix)
**When:** Production is down
**Skip:** Analysis
**Focus:** Reproduce bug test → minimal fix → verify
**Example:** "Users can't login right now"

---

## 🆘 Common Problems & Solutions

### "Skill doesn't seem to activate"
**Solution:** Explicitly mention it:
```
Load the pdca-ai-coding skill and let's implement X
```

### "AI skips writing tests"
**Solution:** Intervene immediately:
```
Stop. Write the failing test first.
```

### "Context window getting full"
**Solution:** Load references one at a time:
```
Just load references/implementation-prompt.md for now
```

### "Not sure which mode to use"
**Solution:** Use this rule:
- <50 lines + no behavior change → **Lite**
- Existing pattern + behavior change → **Lightweight**
- Novel / complex → **Full**
- Production bug → **Emergency**

### "AI doesn't know my project stack"
**Solution:** Either:
- Tell Claude once: "This is a Next.js + TypeScript project"
- Or create `.claude/instructions.md` (see [PROJECT-CONFIGURATION.md](PROJECT-CONFIGURATION.md))

---

## 🎓 Learning Resources

### In Order of Priority

1. **This file** - Quick start ← YOU ARE HERE
2. **[PROJECT-CONFIGURATION.md](PROJECT-CONFIGURATION.md)** - Optional project setup
3. **references/working-agreements.md** - Cheat sheet (print it!)
4. **SKILL.md** - Detailed guide
5. **docs/REFINEMENTS-V1.1.md** - Deep dive

### Original Research

- [InfoQ Article](https://www.infoq.com/articles/PDCA-AI-code-generation/) - The research behind this

---

## 🎯 Your Action Plan

### Right Now (Next 10 Minutes)
- [ ] Upload skill to Claude.ai
- [ ] Review references/working-agreements.md
- [ ] Read working agreements

### Today (Next 2 Hours)
- [ ] Start first coding session
- [ ] Follow all 5 phases
- [ ] Take notes on what happens
- [ ] Complete retrospective

### This Week
- [ ] Do 3-5 coding sessions
- [ ] Run metrics script
- [ ] Update prompts based on retrospectives
- [ ] Share initial results
- [ ] (Optional) Add `.claude/instructions.md` if needed

### This Month
- [ ] Track metrics weekly
- [ ] Customize skill for your project
- [ ] Share with 1-2 teammates
- [ ] Measure impact on velocity

---

## 🚀 Ready to Start?

You have everything you need:
- ✅ The skill is packaged and ready
- ✅ Documentation is comprehensive
- ✅ Scripts are tested and working
- ✅ You know the workflow

**Next step:** Upload `SKILL.md` to Claude.ai

Then say:
```
I need to implement [your feature]. Let's use the PDCA framework.
```

**Let's build better code together! 🎉**

---

Questions? Check the SKILL.md for detailed help.
