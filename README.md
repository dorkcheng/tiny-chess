# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/dorkcheng/tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/dorkcheng/tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A competitive 4KB Python chess engine built for the make.fun [tiny-chess-01 bounty](https://make.fun/bounty/tiny-chess-01).

## Architecture
- `main.py` is strictly under 4,096 bytes as committed, using Python 3.13 standard library only.
- Advanced evaluation: Positional Piece-Square Tables (PST) + MVV-LVA capture scoring + Tactical Blunder Avoidance.
- Deterministic move selection over legal moves provided by the `MAKEFUN_ENV_URL` environment.

## License
MIT
