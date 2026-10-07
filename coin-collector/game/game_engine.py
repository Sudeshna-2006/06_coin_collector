"""
GameEngine: owns the player and all coins.

Tasks implemented:
1. Coins are collected exactly once.
2. Bronze, silver, and gold coin types.
3. Obstacles cost one life and block the player.
4. 30-second countdown and round restart.
"""

"""
GameEngine: owns the player, coins, obstacles, score, lives and timer.
"""

"""
GameEngine: owns the player, coins, obstacles, score, lives and timer.
"""

import random
import pygame

from game.player import Player
from game.coin import Coin
from game.obstacle import Obstacle
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT, draw_scene, draw_text, draw_banner


NUM_COINS = 6
NUM_LIVES = 3
ROUND_DURATION = 30.0

# Obstacles: x, y, width, height
OBSTACLE_LAYOUT = [
    (140, 100, 120, 30),
    (430, 150, 30, 130),
    (250, 350, 160, 30),
    (80, 300, 30, 110),
]

# Coin types: name, value, color
COIN_TYPES = [
    ("bronze", 1, (205, 127, 50)),
    ("silver", 3, (192, 192, 192)),
    ("gold", 5, (255, 215, 0)),
]


class GameEngine:
    def __init__(self):
        self.spawn_x = WIDTH / 2
        self.spawn_y = HEIGHT / 2

        self.obstacles = [
            Obstacle(x, y, width, height)
            for x, y, width, height in OBSTACLE_LAYOUT
        ]

        self._reset_round()

    def _reset_round(self):
        self.player = Player(
            x=self.spawn_x,
            y=self.spawn_y
        )

        # Make sure bronze, silver and gold are all present.
        coin_types = [
            COIN_TYPES[i % len(COIN_TYPES)]
            for i in range(NUM_COINS)
        ]
        random.shuffle(coin_types)

        self.coins = [
            self._random_coin(coin_type)
            for coin_type in coin_types
        ]

        self.score = 0
        self.lives = NUM_LIVES

        self.time_remaining = ROUND_DURATION
        self.round_start_ticks = pygame.time.get_ticks()

        self.game_over = False

        # Prevent losing several lives instantly while holding a key.
        self.last_obstacle_hit = 0
        self.obstacle_cooldown = 500

    def _random_coin(self, coin_type):
        # Try to place the coin outside an obstacle.
        for _ in range(100):
            x = random.randint(30, WIDTH - 30)
            y = random.randint(30, HEIGHT - 30)

            _, value, color = coin_type

            coin = Coin(
                x=x,
                y=y,
                radius=12,
                value=value,
                color=color
            )

            if not any(
                coin.get_rect().colliderect(obstacle.get_rect())
                for obstacle in self.obstacles
            ):
                return coin

        # Fallback if a free position wasn't found.
        _, value, color = coin_type
        return Coin(
            x=30,
            y=30,
            radius=12,
            value=value,
            color=color
        )

    def handle_input(self, keys_pressed):
        # Press R to start a completely new round.
        if keys_pressed[pygame.K_r]:
            self._reset_round()
            return

        if self.game_over:
            return

        dx = 0
        dy = 0

        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed
        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed

        # Remember the old position.
        old_x = self.player.x
        old_y = self.player.y

        # Move the player while respecting screen boundaries.
        self.player.move(dx, dy, WIDTH, HEIGHT)

        # Check obstacle collision using the methods that actually
        # exist in your Player and Obstacle classes.
        hit_obstacle = False

        for obstacle in self.obstacles:
            if self.player.get_rect().colliderect(
                obstacle.get_rect()
            ):
                hit_obstacle = True
                break

        if hit_obstacle:
            # Undo the movement.
            self.player.x = old_x
            self.player.y = old_y

            # Lose only one life per short collision interval.
            now = pygame.time.get_ticks()

            if now - self.last_obstacle_hit >= self.obstacle_cooldown:
                self.lives -= 1
                self.last_obstacle_hit = now

                # Send player back to the starting position.
                self.player.x = self.spawn_x
                self.player.y = self.spawn_y

                if self.lives <= 0:
                    self.lives = 0
                    self.game_over = True

    def update(self):
        if self.game_over:
            return

        # -------------------------
        # TASK 4: 30-SECOND TIMER
        # -------------------------
        elapsed = (
            pygame.time.get_ticks() - self.round_start_ticks
        ) / 1000.0

        self.time_remaining = max(
            0.0,
            ROUND_DURATION - elapsed
        )

        if self.time_remaining <= 0:
            self.time_remaining = 0.0
            self.game_over = True
            return

        # -------------------------
        # TASK 1 + TASK 2:
        # COIN COLLECTION
        # -------------------------

        # check_collection expects the PLAYER and the complete COIN LIST.
        # It returns the coins overlapping the player this frame.
        collected_coins = check_collection(
            self.player,
            self.coins
        )

        # Remove every collected coin immediately.
        # Therefore it can only score once.
        for coin in collected_coins:
            self.score += coin.value
            self.coins.remove(coin)

        # End the round if every coin has been collected.
        if not self.coins:
            self.game_over = True

    def draw(self, screen, font):
        # Draw player, coins and obstacles using the project's renderer.
        draw_scene(
            screen,
            self.player,
            self.coins,
            self.obstacles
        )

        # Display score, lives and remaining time.
        draw_text(
            screen,
            font,
            f"Score: {self.score}",
            (10, 10)
        )

        draw_text(
            screen,
            font,
            f"Lives: {self.lives}",
            (10, 40)
        )

        draw_text(
            screen,
            font,
            f"Time: {int(self.time_remaining + 0.999)}",
            (10, 70)
        )

        # Show the final result when the round ends.
        if self.game_over:
            small_font = pygame.font.Font(None, 30)

            

            draw_banner(
                screen,
                small_font,
                "ROUND OVER"
            )

            draw_text(
                screen,
                small_font,
                f"Final Score: {self.score}",
                (260, 280)
            )

            draw_text(
            screen,
            small_font,
            "Press R to restart",
            (245, 320)
            )