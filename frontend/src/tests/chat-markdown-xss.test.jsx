import { describe, expect, it } from 'vitest';
import { renderMarkdownSafe } from '../components/ChatUI';

describe('markdown sanitization', () => {
  it('strips script tags from markdown output', () => {
    const html = renderMarkdownSafe('hello <script>alert("xss")</script> world');
    expect(html).not.toContain('<script>');
    expect(html).toContain('<p>hello  world</p>');
  });

  it('strips javascript protocol links', () => {
    const html = renderMarkdownSafe('[click me](javascript:alert(1))');
    expect(html).toContain('<a>click me</a>');
    expect(html).not.toContain('javascript:');
  });
});
