#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.authentication.models.roles_positions import RoleManager, Position

print("POSITION_LABELS:")
for key, value in RoleManager.POSITION_LABELS.items():
    print(f"  {key}: {value}")

print(f"\nPosition.OWNER: {Position.OWNER}")
print(f"Position.OWNER.value: {Position.OWNER.value}")

print(f"\nТест форматирования:")
test_position = "owner"
formatted = RoleManager.POSITION_LABELS.get(test_position, test_position)
print(f"  'owner' -> '{formatted}'")
