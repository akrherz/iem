# Delineating Climodat Sites

I can't keep track of how I am managing complexity with the climodat stations,
so perhaps I should document it!

Option | How to Tell?
--- | ---
"real time"? | `online` is True, has `TRACKS_STATION`.
"threaded"? | Third character in ID is `T`.
"spatial averaged"? | Third Character is `C` or ends with `0000`.
"climate site" | If `id` == `climate_site`.

## TODO

- [ ] Threaded sites should not have a `TRACKS_STATION`, but use the `station_threading` table information.
