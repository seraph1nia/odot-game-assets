async () => {
  // Executable mixed-catalog acceptance in the actual browser, not a DOM mock.
  const $ = id => document.getElementById(id), results = [];
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
  const until = async (predicate, description) => {
    const end = Date.now() + 20000;
    while (!predicate()) {
      if (Date.now() > end) throw new Error(`Timeout: ${description}`);
      await delay(100);
    }
  };
  const assert = (condition, description) => {if (!condition) throw new Error(description); results.push(description);};
  const change = (id, value, event = 'change') => {$(id).value = value; $(id).dispatchEvent(new Event(event));};
  const root = new URL('./', document.baseURI);
  const metadata = await (await fetch(new URL('catalog.json', root))).json();
  const ui = metadata.assets.filter(asset => asset.kind);
  assert(metadata.schema_version === 2 && ui.length === 13, 'Generated v2 catalog advertises exactly 13 distinct shipped UI resources/examples');
  if ($('detail').open) $('close').click();
  change('search', 'ui/', 'input'); change('category', '');
  $('animated').checked = false; $('animated').dispatchEvent(new Event('change'));
  assert(document.querySelectorAll('.card').length === ui.length, 'UI entries discoverable through ordinary search');
  assert(!document.querySelector('model-viewer'), 'UI grid creates no model viewers');
  let downloadHash = null;
  for (const asset of ui) {
    document.querySelector(`[data-id="${asset.id}"]`).click();
    const image = $('viewer-host').querySelector('img');
    await until(() => image?.complete && image.naturalWidth > 0, `${asset.id} native image`);
    assert(!document.querySelector('model-viewer') && $('animations').hidden && document.querySelector('.camera-controls').hidden,
      `${asset.id}: image/resource dispatch, no 3D/animation controls`);
    assert(image.alt === asset.preview_label && $('load-status').textContent === asset.preview_label,
      `${asset.id}: truthful preview identity/label`);
    assert(!asset.model && $('links').textContent.includes('Download runtime UI package'), `${asset.id}: shared payload accessible`);
    if (asset.role === 'showcase') {
      assert(!asset.resource && !$('links').textContent.includes('Native resource') && $('resource-note').textContent.includes('Authoring-only composition') && $('stats').textContent.includes('Authoring-only prototype'),
        `${asset.id}: showcase is not advertised as a new runtime component/download`);
    }
    for (const link of $('links').querySelectorAll('a')) {
      const url = new URL(link.href);
      assert(url.origin === location.origin && url.pathname.startsWith(root.pathname), `${asset.id}: portable subpath link ${link.textContent}`);
      const response = await fetch(url);
      assert(response.ok, `${asset.id}: actual link fetch ${link.textContent}`);
      if (link.textContent.includes('runtime UI package')) {
        const bytes = await response.arrayBuffer();
        const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n => n.toString(16).padStart(2, '0')).join('');
        assert(hash === asset.package.version, `${asset.id}: downloaded package bytes match generated manifest`);
        if (downloadHash) assert(downloadHash === hash, `${asset.id}: no duplicate per-item bundle`);
        downloadHash = hash;
      }
    }
    if (asset.role === 'art') {
      assert(image.naturalWidth === 192 && image.naturalHeight === 192 && $('viewer-host').classList.contains('alpha-view'), 'Original seal native PNG and alpha-aware presentation');
    }
    $('close').click();
  }
  for (const asset of ui) {
    for (const alias of asset.aliases) {
      for (const query of new Set([alias, alias.replaceAll('-', ' '), alias.toUpperCase()])) {
        change('search', query, 'input');
        const cards = [...document.querySelectorAll('.card')];
        assert(cards.length === 1 && cards[0].dataset.id === asset.id,
          `Inventory alias ${query} finds ${asset.id}, not an invented component`);
        assert(new URL(location.href).searchParams.get('q') === query,
          `Inventory alias ${query} is preserved in the URL`);
      }
    }
  }
  change('search', '', 'input'); change('category', 'ui/components');
  assert(document.querySelectorAll('.card').length === 9, 'UI component category contains nine reusable native scenes');
  $('animated').checked = true; $('animated').dispatchEvent(new Event('change'));
  assert(document.querySelectorAll('.card').length === 0, 'UI resources do not acquire fictitious model animations');
  $('animated').checked = false; $('animated').dispatchEvent(new Event('change')); change('category', '');
  const model = metadata.assets.find(asset => asset.id === 'props/sword');
  document.querySelector(`[data-id="${model.id}"]`).click();
  await until(() => document.querySelector('model-viewer')?.loaded, 'preserved GLB after UI');
  assert(!document.querySelector('.camera-controls').hidden && !$('preview-section').hidden && !$('reference-section').hidden,
    'Switching UI back to actual GLB restores model controls and companion views');
  $('close').click();
  return {checks: results.length, package_sha256: downloadHash, results};
}
