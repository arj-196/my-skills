#!/usr/bin/env bash
#
# unify-grill.sh — Regenerate the self-contained `/grill` skill from its sources.
#
# `/grill` is a *build artifact*: a flattened copy of the modular
# `/grill-with-docs` skill, which itself is just a wrapper that pulls in
# `/grilling` and `/domain-modeling` (and the format files those reference).
#
# When you edit any of the source skills, run this script to rebuild `/grill`
# so it stays in sync. It drives `claude -p` (headless) to do the inlining.
#
# Usage:
#   ~/.agents/unify-grill.sh
#
set -euo pipefail

SKILLS_DIR="${HOME}/.agents/skills"

# The modular source skill and the skills it composes.
WRAPPER_SKILL="grill-with-docs"   # the thin wrapper that references the others
SOURCE_SKILLS=("grilling" "domain-modeling")
TARGET_SKILL="grill"              # the flattened, self-contained output

# --- sanity checks ---------------------------------------------------------
for s in "$WRAPPER_SKILL" "${SOURCE_SKILLS[@]}"; do
  if [[ ! -f "${SKILLS_DIR}/${s}/SKILL.md" ]]; then
    echo "error: source skill '${s}' not found at ${SKILLS_DIR}/${s}/SKILL.md" >&2
    exit 1
  fi
done

if ! command -v claude >/dev/null 2>&1; then
  echo "error: 'claude' CLI not found on PATH" >&2
  exit 1
fi

echo "Regenerating /${TARGET_SKILL} from /${WRAPPER_SKILL} (+ ${SOURCE_SKILLS[*]})..."

# --- the task prompt -------------------------------------------------------
read -r -d '' PROMPT <<PROMPT_EOF || true
You are performing a deterministic skill-flattening task.

Goal: regenerate the skill at ${SKILLS_DIR}/${TARGET_SKILL}/ so it is a single,
fully self-contained copy of the modular ${SKILLS_DIR}/${WRAPPER_SKILL}/ skill —
with every reference resolved and inlined, and zero pointers left to chase.

Steps:
1. Read ${SKILLS_DIR}/${WRAPPER_SKILL}/SKILL.md. It is a thin wrapper that just
   tells Claude to run one skill using another (currently /grilling and
   /domain-modeling). Note which skills it composes and its frontmatter
   (especially 'disable-model-invocation').
2. Read the SKILL.md of every skill it references: ${SOURCE_SKILLS[*]}.
3. Follow and read EVERY file those SKILL.md files link to (e.g. format specs
   like CONTEXT-FORMAT.md and ADR-FORMAT.md). Anything referenced must end up
   inlined — the output must not link out to any sibling file.
4. Write ${SKILLS_DIR}/${TARGET_SKILL}/SKILL.md containing ALL of that guidance
   merged into one coherent document. Requirements:
     - Frontmatter: name must be '${TARGET_SKILL}'. Reuse the
       '${WRAPPER_SKILL}' description and keep 'disable-model-invocation: true'
       if the wrapper has it.
     - Preserve the behaviour and instructions of the source skills faithfully.
       Do not add new behaviour, drop guidance, or editorialise. Merge, don't
       rewrite: keep the wording of the sources except where light stitching is
       needed to make one flowing document (e.g. resolving "use the X skill"
       into the inlined content, or "see FILE.md" into the inlined section).
     - Replace every cross-skill and cross-file reference with the actual
       inlined content. No links to CONTEXT-FORMAT.md, ADR-FORMAT.md, or other
       skills should remain.
5. Also mirror ${SKILLS_DIR}/${WRAPPER_SKILL}/agents/openai.yaml to
   ${SKILLS_DIR}/${TARGET_SKILL}/agents/openai.yaml, but change the
   display_name to reflect the '${TARGET_SKILL}' name and keep the same policy
   (e.g. allow_implicit_invocation: false).

Overwrite the target files if they already exist. Report a one-line summary of
what changed when done.
PROMPT_EOF

# --- run headless ----------------------------------------------------------
# acceptEdits auto-approves file writes; restrict tools to what the task needs.
claude -p "${PROMPT}" \
  --permission-mode acceptEdits \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep"

echo "Done. Review the result:"
echo "  ${SKILLS_DIR}/${TARGET_SKILL}/SKILL.md"
