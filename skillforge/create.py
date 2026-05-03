from __future__ import annotations

import re

from .catalog import REPO_ROOT, SKILLS_DIR, slug_title
from .validate import NAME_PATTERN, validate_skill


TEMPLATE_DIR = REPO_ROOT / "skillforge" / "templates" / "skill"
SKILL_TEMPLATE_PATH = TEMPLATE_DIR / "SKILL.md.tmpl"
README_TEMPLATE_PATH = TEMPLATE_DIR / "README.md.tmpl"
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}\n]+\}\}")


def one_line(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def placeholder(name: str) -> str:
    return "{{" + name + "}}"


def yaml_list(values: list[str], placeholder_name: str) -> str:
    items = [one_line(value) for value in values if one_line(value)] or [placeholder(placeholder_name)]
    return "\n".join(f"  - {item}" for item in items)


def render_template(template: str, context: dict[str, str]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def unresolved_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_PATTERN.findall(text)))


def create_skill(
    skill_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    owner: str | None = None,
    categories: list[str] | None = None,
    tags: list[str] | None = None,
    risk_level: str | None = None,
    force: bool = False,
) -> dict:
    skill_id = one_line(skill_id)
    if not NAME_PATTERN.match(skill_id):
        raise ValueError("Skill ID must be lowercase kebab-case letters, digits, and hyphens")

    skill_dir = SKILLS_DIR / skill_id
    if skill_dir.exists() and not force:
        raise FileExistsError(f"Skill already exists: {skill_dir}. Use --force to replace it.")

    if skill_dir.exists() and force:
        for child in sorted(skill_dir.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
        skill_dir.rmdir()

    skill_title = one_line(title) or slug_title(skill_id)
    description_text = one_line(description) or placeholder("description")
    short_description = description_text if description else placeholder("short_description")
    expanded_description = description_text if description else placeholder("expanded_description")
    owner_text = one_line(owner) or placeholder("owner")
    category_values = categories or []
    tag_values = tags or []
    risk_text = one_line(risk_level) or placeholder("risk_level")
    search_query = description_text if description else skill_id.replace("-", " ")

    aliases = [skill_id, skill_title] if title else [skill_id]
    aliases.extend([placeholder("alias_one"), placeholder("alias_two")])

    context = {
        "skill_id": skill_id,
        "skill_title": skill_title,
        "description": description_text,
        "owner": owner_text,
        "short_description": short_description,
        "expanded_description": expanded_description,
        "aliases_yaml": yaml_list(aliases, "alias"),
        "categories_yaml": yaml_list(category_values, "category"),
        "tags_yaml": yaml_list(tag_values, "tag"),
        "tasks_yaml": yaml_list([placeholder("task_one"), placeholder("task_two"), placeholder("task_three")], "task"),
        "use_when_yaml": yaml_list([placeholder("use_when_one"), placeholder("use_when_two")], "use_when"),
        "do_not_use_when_yaml": yaml_list([placeholder("do_not_use_when_one")], "do_not_use_when"),
        "inputs_yaml": yaml_list([placeholder("input_one"), placeholder("input_two")], "input"),
        "outputs_yaml": yaml_list([placeholder("output_one"), placeholder("output_two")], "output"),
        "examples_yaml": yaml_list([placeholder("llm_example_prompt_one"), placeholder("llm_example_prompt_two"), placeholder("llm_example_prompt_three")], "example"),
        "related_skills_yaml": yaml_list([placeholder("related_skill_one")], "related_skill"),
        "risk_level": risk_text,
        "permissions_yaml": yaml_list([placeholder("permission_one"), placeholder("permission_two")], "permission"),
        "page_title": f"{skill_title} Skill - SkillForge",
        "meta_description": short_description,
        "workflow_goal": description_text if description else placeholder("workflow_goal"),
        "method_or_workflow": placeholder("method_or_workflow"),
        "input_one": placeholder("input_one"),
        "input_two": placeholder("input_two"),
        "input_three": placeholder("input_three"),
        "output_one": placeholder("output_one"),
        "output_two": placeholder("output_two"),
        "output_three": placeholder("output_three"),
        "llm_example_prompt_one": placeholder("llm_example_prompt_one"),
        "llm_example_prompt_two": placeholder("llm_example_prompt_two"),
        "one_or_two_sentence_value_proposition": description_text if description else placeholder("one_or_two_sentence_value_proposition"),
        "skill_repo_url": f"https://github.com/medatasci/agent_skills/tree/main/skills/{skill_id}",
        "parent_package_name": "SkillForge",
        "parent_package_repo_url": "https://github.com/medatasci/agent_skills",
        "distribution_context": "SkillForge Agent Skills Marketplace",
        "version_or_release_channel": "main",
        "parent_collection_name": "SkillForge",
        "parent_collection_url": "https://github.com/medatasci/agent_skills",
        "skill_categories": ", ".join(category_values) if category_values else placeholder("skill_categories"),
        "collection_context": placeholder("collection_context"),
        "what_the_skill_does": description_text if description else placeholder("what_the_skill_does"),
        "call_reason_one": placeholder("call_reason_one"),
        "call_reason_two": placeholder("call_reason_two"),
        "call_reason_three": placeholder("call_reason_three"),
        "primary_use_case": placeholder("primary_use_case"),
        "secondary_use_case": placeholder("secondary_use_case"),
        "tertiary_use_case": placeholder("tertiary_use_case"),
        "do_not_use_case_one": placeholder("do_not_use_case_one"),
        "do_not_use_case_two": placeholder("do_not_use_case_two"),
        "keywords": ", ".join([skill_id, *category_values, *tag_values]) if category_values or tag_values else placeholder("keywords"),
        "search_terms": placeholder("search_terms"),
        "search_query": search_query,
        "option_one": placeholder("option_one"),
        "option_two": placeholder("option_two"),
        "option_three": placeholder("option_three"),
        "configuration_item_one": placeholder("configuration_item_one"),
        "configuration_item_two": placeholder("configuration_item_two"),
        "output_location_one": placeholder("output_location_one"),
        "output_location_two": placeholder("output_location_two"),
        "llm_example_prompt_three": placeholder("llm_example_prompt_three"),
        "llm_example_prompt_four": placeholder("llm_example_prompt_four"),
        "getting_started_prompt": f"Use {skill_id} to {placeholder('getting_started_goal')}.",
        "user_should_provide_one": placeholder("user_should_provide_one"),
        "user_should_provide_two": placeholder("user_should_provide_two"),
        "help_case_one": placeholder("help_case_one"),
        "help_case_two": placeholder("help_case_two"),
        "help_case_three": placeholder("help_case_three"),
        "llm_call_goal": placeholder("llm_call_goal"),
        "task_based_llm_prompt": placeholder("task_based_llm_prompt"),
        "guardrail_instruction": placeholder("guardrail_instruction"),
        "task_description": placeholder("task_description"),
        "data_handling": placeholder("data_handling"),
        "writes_vs_read_only": placeholder("writes_vs_read_only"),
        "external_services": placeholder("external_services"),
        "credential_requirements": placeholder("credential_requirements"),
        "approval_gate_one": placeholder("approval_gate_one"),
        "approval_gate_two": placeholder("approval_gate_two"),
        "feedback_url": "https://github.com/medatasci/agent_skills/issues/new/choose",
        "feedback_case_one": "The skill helped but should be easier to find.",
        "feedback_case_two": "The skill failed, confused you, or missed the workflow.",
        "feedback_case_three": "You have an idea for a better related workflow.",
        "example_feedback_problem": placeholder("example_feedback_problem"),
        "author": owner_text if owner else placeholder("author"),
        "maintainer_status": placeholder("maintainer_status"),
        "citations_or_not_applicable": placeholder("citations_or_not_applicable"),
        "related_skill_one": placeholder("related_skill_one"),
        "related_skill_one_reason": placeholder("related_skill_one_reason"),
        "related_skill_two": placeholder("related_skill_two"),
        "related_skill_two_reason": placeholder("related_skill_two_reason"),
        "related_skill_three": placeholder("related_skill_three"),
        "related_skill_three_reason": placeholder("related_skill_three_reason"),
    }

    skill_dir.mkdir(parents=True, exist_ok=False)
    skill_template = SKILL_TEMPLATE_PATH.read_text(encoding="utf-8")
    readme_template = README_TEMPLATE_PATH.read_text(encoding="utf-8")
    skill_text = render_template(skill_template, context)
    readme_text = render_template(readme_template, context)
    (skill_dir / "SKILL.md").write_text(skill_text.rstrip() + "\n", encoding="utf-8")
    (skill_dir / "README.md").write_text(readme_text.rstrip() + "\n", encoding="utf-8")

    validation = validate_skill(skill_dir)
    placeholder_files = {
        "SKILL.md": unresolved_placeholders(skill_text),
        "README.md": unresolved_placeholders(readme_text),
    }
    return {
        "skill_id": skill_id,
        "skill_dir": str(skill_dir),
        "files": [str(skill_dir / "SKILL.md"), str(skill_dir / "README.md")],
        "validation": {
            "ok": validation.ok,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        "placeholders_remaining": {
            file_name: placeholders
            for file_name, placeholders in placeholder_files.items()
            if placeholders
        },
        "next_commands": [
            "python -m skillforge build-catalog",
            f"python -m skillforge evaluate {skill_id} --json",
        ],
    }
