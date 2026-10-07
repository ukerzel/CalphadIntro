import type { LearningID } from '@/lib/learning';
import { colabURL, notebooks } from '@/lib/lesson-meta';

/** Google's official "Open in Colab" badge, linking one course notebook (the image loads from Colab). */
export const COLAB_BADGE = 'https://colab.research.google.com/assets/colab-badge.svg';
export function ColabButton({ file, title }: { file: string; title: string }) {
  return <a className="colab-button" href={colabURL(file)} target="_blank" rel="noreferrer" title={`Open “${title}” in Colab (new tab)`}>
    <img src={COLAB_BADGE} alt={`Open “${title}” in Colab`} width={117} height={20} loading="lazy" />
  </a>;
}

/** "Run it yourself": the step's course notebooks in Colab, or locally with Jupyter. Lives on the lab card, after the attempt. */
export default function NotebookLinks({ id, compact = false }: { id: LearningID; compact?: boolean }) {
  const list = notebooks[id];
  if (!list?.length) return null;
  if (compact) return <div className="notebook-compact" aria-label="Run it yourself in a notebook">
    {list.map(([file, title]) => <ColabButton key={file} file={file} title={title} />)}
  </div>;
  return <section className="notebook-links" aria-label="Run it yourself">
    <p className="dock-views-title">Run it yourself:</p>
    <ul>{list.map(([file, title]) => <li key={file}>
      <span className="notebook-title">{title}</span>
      <ColabButton file={file} title={title} />
      <span className="caption">or on your computer: <code>poetry run jupyter lab notebooks/{file}.ipynb</code></span>
    </li>)}</ul>
    <p className="caption">Each notebook asks you to try a calculation before it shows the course result.</p>
  </section>;
}
