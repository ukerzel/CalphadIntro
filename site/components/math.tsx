import katex from 'katex';

const cache = new Map<string, string>();
/** KaTeX markup (HTML plus MathML for screen readers). Narration TeX is validated at sync time. */
function markup(tex: string, display: boolean): string {
  const key = `${display ? 'D' : 'I'}${tex}`;
  let html = cache.get(key);
  if (html === undefined) {
    html = katex.renderToString(tex, { displayMode: display, output: 'htmlAndMathml', throwOnError: false, strict: 'ignore' });
    cache.set(key, html);
  }
  return html;
}

export default function Tex({ tex, display = false }: { tex: string; display?: boolean }) {
  return <span className={display ? 'math math-display' : 'math'} dangerouslySetInnerHTML={{ __html: markup(tex, display) }} />;
}
