(function () {
  const root = document.querySelector('[data-shows-root]');
  if (!root) {
    return;
  }

  const sourceUrl = root.getAttribute('data-source-url') || '';
  const list = root.querySelector('[data-shows-list]');
  const status = root.querySelector('[data-shows-status]');

  const setStatus = (text) => {
    if (status) {
      status.textContent = text;
    }
  };

  const parseCsv = (text) => {
    const rows = [];
    let row = [];
    let cell = '';
    let inQuotes = false;

    for (let i = 0; i < text.length; i += 1) {
      const ch = text[i];
      const next = text[i + 1];

      if (inQuotes) {
        if (ch === '"' && next === '"') {
          cell += '"';
          i += 1;
        } else if (ch === '"') {
          inQuotes = false;
        } else {
          cell += ch;
        }
        continue;
      }

      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        row.push(cell.trim());
        cell = '';
      } else if (ch === '\n') {
        row.push(cell.trim());
        rows.push(row);
        row = [];
        cell = '';
      } else if (ch !== '\r') {
        cell += ch;
      }
    }

    if (cell.length || row.length) {
      row.push(cell.trim());
      rows.push(row);
    }

    return rows;
  };

  const normalizeHeader = (value) =>
    value
      .toLowerCase()
      .replace(/\uFEFF/g, '')
      .replace(/\s+/g, '_')
      .trim();

  const parseDate = (value) => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const isFalseLike = (value) => {
    const normalized = (value || '').trim().toLowerCase();
    return normalized === 'false' || normalized === '0' || normalized === 'no' || normalized === 'nein';
  };

  const renderShows = (shows) => {
    if (!list) {
      return;
    }

    if (shows.length === 0) {
      setStatus('Neue Shows werden bald announced.');
      return;
    }

    setStatus('');

    list.innerHTML = shows
      .map((show) => {
        const safeTitle = show.title || 'Urbanism Live';
        const safeCity = show.city || 'TBA';
        const safeVenue = show.venue || 'Venue TBA';
        const safeDate = show.show_date || '';
        const notesHtml = show.notes ? `<p class="notes">${show.notes}</p>` : '';
        const ticketHtml = show.ticket_url
          ? `<a class="ticket" href="${show.ticket_url}" target="_blank" rel="noreferrer">Tickets</a>`
          : '<span class="ticket ticket-disabled">Info folgt</span>';

        return `\n          <li>\n            <div>\n              <p class="show-date">${safeDate}</p>\n              <h3>${safeTitle}</h3>\n              <p>${safeCity} · ${safeVenue}</p>\n              ${notesHtml}\n            </div>\n            ${ticketHtml}\n          </li>\n        `;
      })
      .join('');
  };

  const rowsToShows = (rows) => {
    if (rows.length < 2) {
      return [];
    }

    const headers = rows[0].map(normalizeHeader);
    const headerIndex = new Map(headers.map((h, idx) => [h, idx]));

    const required = ['show_date', 'title', 'city', 'venue'];
    if (!required.every((h) => headerIndex.has(h))) {
      setStatus('Google Sheet hat nicht die erwarteten Spalten.');
      return [];
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return rows
      .slice(1)
      .filter((row) => row.some((value) => value && value.length > 0))
      .map((row) => {
        const get = (name) => row[headerIndex.get(name)] || '';
        return {
          show_date: get('show_date'),
          title: get('title'),
          city: get('city'),
          venue: get('venue'),
          ticket_url: get('ticket_url'),
          notes: get('notes'),
          active: get('active'),
        };
      })
      .filter((show) => !isFalseLike(show.active))
      .filter((show) => {
        const parsed = parseDate(show.show_date);
        return parsed && parsed >= today;
      })
      .sort((a, b) => {
        const dateA = parseDate(a.show_date);
        const dateB = parseDate(b.show_date);
        return dateA - dateB;
      });
  };

  const load = async () => {
    if (!sourceUrl || sourceUrl.includes('PASTE_')) {
      setStatus('Sheet-Quelle fehlt. Trage die veröffentlichte Google-Sheet-CSV-URL ein.');
      return;
    }

    try {
      setStatus('Shows werden geladen ...');
      const response = await fetch(sourceUrl, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const csv = await response.text();
      const shows = rowsToShows(parseCsv(csv));
      renderShows(shows);
    } catch (error) {
      setStatus('Shows konnten nicht geladen werden. Bitte später erneut versuchen.');
    }
  };

  load();
})();
