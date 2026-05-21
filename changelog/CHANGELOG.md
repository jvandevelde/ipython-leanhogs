# Changelog

## May 2026
Replaced the Quandl API dependency with direct reading from a user-maintained Excel settlement file (`hog_settlements.xlsx`), removing the need for API credentials or cached pickle files entirely. The UI was rebuilt with a custom-styled panel featuring structured sections, inline status feedback, and a native file picker for selecting the data source. Butterfly spread validation was also hardened to catch invalid contract selections (e.g. duplicate legs) with a clear error message rather than a silent crash.
