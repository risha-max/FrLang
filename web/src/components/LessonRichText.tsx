import { Fragment, type ReactNode } from "react";

const TOKEN_RE = /`([^`]+)`/g;

type LessonRichTextProps = {
  text: string;
  as?: "p" | "span" | "li";
  className?: string;
};

/** Affiche le texte pédagogique en mettant les allusions FrLang (`mot`) en évidence. */
export function LessonRichText({
  text,
  as: Tag = "span",
  className,
}: LessonRichTextProps) {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  const pattern = new RegExp(TOKEN_RE.source, "g");

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(
        <Fragment key={`t-${lastIndex}`}>
          {text.slice(lastIndex, match.index)}
        </Fragment>,
      );
    }
    nodes.push(
      <code key={`c-${match.index}`} className="frlang-token" translate="no">
        {match[1]}
      </code>,
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    nodes.push(
      <Fragment key={`t-${lastIndex}`}>{text.slice(lastIndex)}</Fragment>,
    );
  }

  return <Tag className={className}>{nodes}</Tag>;
}
