// Static app domains only. Existing GitHub publishing pipelines remain the source.
// The apps host serves the site root (the app index); each app keeps its own host.
const APPS = Object.freeze({
  'apps.codekino.org': '/',
  'backloggy.codekino.org': '/backloggy/',
  'bindr.codekino.org': '/bindr/',
  'panju.codekino.org': '/panju/'
});
// Retired hostnames: permanently redirected to the app's current host.
const MOVED = Object.freeze({
  'pokebindr.codekino.org': 'bindr.codekino.org'
});
const ORIGIN = 'https://herickchann.github.io';
export default {
  async fetch(request) {
    const incoming = new URL(request.url), prefix = APPS[incoming.hostname];
    const moved = MOVED[incoming.hostname];
    if (moved) { incoming.hostname = moved; return Response.redirect(incoming.href, 301); }
    if (!prefix) return new Response('Not found', {status:404});
    const isRoot = prefix === '/';
    if (!['GET','HEAD'].includes(request.method)) return new Response('Method not allowed', {status:405, headers:{Allow:'GET, HEAD'}});
    // Accept older absolute asset paths as well as the new root-relative paths.
    const path = incoming.pathname.startsWith(prefix) ? incoming.pathname : prefix + incoming.pathname.slice(1);
    const upstream = new URL(path + incoming.search, ORIGIN);
    if (!upstream.pathname.startsWith(prefix)) return new Response('Invalid path', {status:400});
    const headers = new Headers();
    for (const name of ['Accept','Accept-Encoding','Accept-Language','Range','If-None-Match','If-Modified-Since','Cache-Control','Pragma']) {
      const value = request.headers.get(name); if (value) headers.set(name, value);
    }
    // Never send the app domain's cookies or credentials to the static origin.
    let response;
    try {
      response = await fetch(upstream, {method:request.method, headers, redirect:'manual'});
      if (!isRoot && response.status === 404 && request.headers.get('Accept')?.includes('text/html') && !/\.[^/]+$/.test(incoming.pathname)) {
        response = await fetch(new URL(prefix + 'index.html', ORIGIN), {method:request.method, headers, redirect:'manual'});
      }
    } catch { return new Response('The app is temporarily unavailable. Please try again shortly.', {status:502}); }
    const result = new Response(response.body, response);
    const location = result.headers.get('Location');
    if (location) {
      const destination = new URL(location, upstream);
      if (destination.origin === ORIGIN && destination.pathname.startsWith(prefix)) {
        destination.protocol = incoming.protocol; destination.host = incoming.host;
        destination.pathname = '/' + destination.pathname.slice(prefix.length);
        result.headers.set('Location', destination.href);
      }
    }
    if (!isRoot && request.method !== 'HEAD' && result.headers.get('Content-Type')?.includes('text/html') && result.status === 200) {
      result.headers.delete('ETag'); result.headers.delete('Content-Length');
      return new HTMLRewriter().on('base', {element(element) { element.setAttribute('href','/'); }}).transform(result);
    }
    return result;
  }
};
