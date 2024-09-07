# Manufactured Housing Communities Michigan Mapping Tool
***This app is a visualization tool designed to visualize the distribution of manufactured housing communities across Michigan. LARA data was obtained in January 2024 from the Michigan Department of Licensing and Regulatory Affairs via a Freedom of Information Act (FOIA) Request. MHVillage data was scraped in December 2023. For more information, visit MHAction.org.***

## Remaining issues
- ipywidgets and ipyleaflet versioning leads to issues with marker cluster/popup function.
- Create a table download with all counties, house district, or senate district rows.

## References
- Using deploy.yml for shinylive: https://github.com/wch/shinylive-example/blob/main/.github/workflows/deploy.yml
- IpyLeaflet Documentation: https://ipyleaflet.readthedocs.io/en/latest/
- IpyLeaflet GeoJSON Handling: https://github.com/jupyter-widgets/ipyleaflet/blob/master/examples/CountriesGeoJSON.ipynb
- ShinyPy Documentation: https://shiny.posit.co/py/docs/overview.html
- Plotly Package Documentation: https://plotly.com/python/bar-charts/
- Hosting on GitHub Pages: https://www.appsilon.com/post/shiny-for-python-deploy-github-pages and https://github.com/RamiKrispin/shinylive
