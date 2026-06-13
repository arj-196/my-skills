# Makefile for managing agent skills.
#
# Skills live in .agents/skills/ and are exposed to Claude Code by symlinking
# them into ~/.claude/skills/. The `sync` target makes sure a symlink exists in
# ~/.claude/skills/ for every skill found in .agents/skills/.

AGENTS_DIR    := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
SKILLS_DIR    := $(AGENTS_DIR)/skills
CLAUDE_SKILLS := $(HOME)/.claude/skills

# Relative link target so the symlinks stay portable if $HOME moves.
REL_PREFIX    := ../../.agents/skills

.PHONY: sync sync-check

## sync: create a symlink in ~/.claude/skills for every skill in .agents/skills
sync:
	@mkdir -p "$(CLAUDE_SKILLS)"
	@for skill in "$(SKILLS_DIR)"/*/; do \
		[ -d "$$skill" ] || continue; \
		name=$$(basename "$$skill"); \
		link="$(CLAUDE_SKILLS)/$$name"; \
		target="$(REL_PREFIX)/$$name"; \
		if [ -L "$$link" ]; then \
			if [ -e "$$link" ]; then \
				printf '  ok    %s\n' "$$name"; \
			else \
				ln -sfn "$$target" "$$link"; \
				printf '  fixed %s (was broken)\n' "$$name"; \
			fi; \
		elif [ -e "$$link" ]; then \
			printf '  SKIP  %s (exists and is not a symlink)\n' "$$name"; \
		else \
			ln -s "$$target" "$$link"; \
			printf '  link  %s\n' "$$name"; \
		fi; \
	done

## sync-check: report which skills are missing symlinks without changing anything
sync-check:
	@for skill in "$(SKILLS_DIR)"/*/; do \
		[ -d "$$skill" ] || continue; \
		name=$$(basename "$$skill"); \
		link="$(CLAUDE_SKILLS)/$$name"; \
		if [ -e "$$link" ] || [ -L "$$link" ]; then \
			printf '  ok      %s\n' "$$name"; \
		else \
			printf '  MISSING %s\n' "$$name"; \
		fi; \
	done
