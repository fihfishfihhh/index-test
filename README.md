# FIH Community - Geometry Dash Hub

Static React site (React + Tailwind + Babel via CDN, no build step).

```
index.html
css/style.css
js/data.js              # mock data
js/app.jsx              # state + handlers, mounts <App />
js/components/*.jsx     # Header, Sidebar and one component per tab
```

Because the `.jsx` files are loaded by Babel in the browser, serve the folder over HTTP
(opening `index.html` with `file://` will not work):

```
python3 -m http.server 8000
```
