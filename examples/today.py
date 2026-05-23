"""Render today's solved puzzle. Press Play in the prototype to see it."""

from datetime import date

from cadbuildr.foundation import show

from a_puzzle_a_day import APuzzleADaySolved

today = date.today()
show(APuzzleADaySolved(month=today.month, day=today.day))
