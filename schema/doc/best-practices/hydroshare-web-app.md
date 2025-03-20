# Web App Connector

### Complete Example for a HydroShare Web App Connector

```json
{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "CUAHSI JupyterHub",
  "description": "A web-based Jupyter computing environment suitable for scientific research",
  "image": "https://example.com/icon.png",
  "url": "https://example.com",
  "version": "1.0.0",
  "author": {
    "@type": "Organization",
    "name": "ABC Tools"
  },
  "encodingFormat": [
    "application/x-ipynb+json",
    "text/csv"
  ],
  "audience": [
    {
    "@type": "Audience",
    "name": "Sharing Status",
    "audienceType": ["private", "public", "published"]
    },
    {
    "@type": "Audience",
    "name": "Support",
    "audienceType": ["Resource", "Collection"]
    }
  ],
  "potentialAction": [
    {
    "@type": "ViewAction",
    "name": "App-launching File Level URL Pattern",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://jupyterhub.cuahsi.org/hub/spawn?next=/user-redirect/nbfetch/hs-pull?id=${HS_RES_ID}%26start%3D${HS_FILE_PATH}%26app%3Dlab",
      "actionPlatform": "http://schema.org/DesktopWebPlatform"
    },
    "query-input": [
      "required name=HS_RES_ID",
      "required name=HS_FILE_PATH"
    ]
   },
   {
    "@type": "ViewAction",
    "name": "App-launching Resource Level URL Pattern",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://jupyterhub.cuahsi.org/hub/spawn?next=/user-redirect/nbfetch/hs-pull?id=${HS_RES_ID}%26app%3Dlab%0A",
      "actionPlatform":  "http://schema.org/DesktopWebPlatform"
    },
    "query-input": [
      "required name=HS_RES_ID"
    ]
  }
]   
}
```

