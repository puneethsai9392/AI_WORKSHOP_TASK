
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function cleanMarkdown(content = "") {
  return content
    // Convert escaped table pipes to normal pipes
    .replace(/\\\|/g, "|")

    // Convert HTML line breaks to newlines
    .replace(/\\?<br\s*\/?>/gi, "\n")

    // Remove backslash line continuations
    .replace(/\\[ \t]*\r?\n/g, "\n");
}

export default function MarkdownResponse({ content }) {
  const cleaned = cleanMarkdown(content);

  return (
    <div className="markdown-response">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          hr: () => null,
        }}
      >
        {cleaned}
      </ReactMarkdown>
    </div>
  );
}
