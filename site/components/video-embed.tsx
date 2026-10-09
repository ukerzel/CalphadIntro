'use client';
/** Two-click video: a local placeholder first, the YouTube player only after the learner presses play.
 *  `compact` is the one-line version at the top of a step: the row itself is the play button. */
import { useState } from 'react';
import { ArrowUpRight, Play } from 'lucide-react';
import { youtubeEmbed, youtubeWatch } from '@/lib/media';

const NOTE = 'Pressing play loads the video from YouTube (Google). Nothing is loaded before that.';

export default function VideoEmbed({ youtube, title, compact = false }: { youtube: string; title: string; compact?: boolean }) {
  const [on, setOn] = useState(false);
  const play = <button type="button" className={compact ? 'video-row' : 'video-poster'} onClick={() => setOn(true)} aria-label={`Play “${title}” (loads the YouTube player)`}>
    <span className="video-play" aria-hidden><Play /></span>
    {compact ? <span className="video-row-text"><span className="video-row-title">Watch · {title}</span><span className="video-note">{NOTE}</span></span>
      : <><span className="video-title">{title}</span><span className="video-note">{NOTE}</span></>}
  </button>;
  const frame = <div className="video-frame"><iframe src={youtubeEmbed(youtube)} title={title} allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowFullScreen referrerPolicy="strict-origin-when-cross-origin" /></div>;
  return <figure className={`video-embed${compact ? ' is-compact' : ''}`}>
    {compact ? (on ? frame : play) : on ? frame : <div className="video-frame">{play}</div>}
    <figcaption className="caption">Prefer YouTube itself? <a href={youtubeWatch(youtube)} target="_blank" rel="noreferrer">Watch it there<ArrowUpRight aria-hidden className="inline-icon" /></a></figcaption>
  </figure>;
}
