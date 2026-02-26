"""Tests for pgchess.gui.sprites: sprite loading, caching, and scaling."""
from unittest.mock import patch, MagicMock

import pygame

from pgchess.gui.sprites import Sprites, _load_sprite


class TestLoadSprite:
    """Test the module-level _load_sprite helper."""

    def test_loads_and_converts_alpha(self):
        """_load_sprite should load from the resolved path and call convert_alpha."""
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface

        with patch('pgchess.gui.sprites.get_resource_path', return_value='/resolved/img.png'):
            with patch('pgchess.gui.sprites.pygame.image.load', return_value=mock_surface) as mock_load:
                result = _load_sprite('assets/images/img.png')
                mock_load.assert_called_once_with('/resolved/img.png')
                mock_surface.convert_alpha.assert_called_once()
                assert result == mock_surface


class TestSpritesInit:
    """Test the Sprites class initialization."""

    def test_loads_all_12_piece_sprites(self):
        """Constructor should load sprites for all 12 piece codes."""
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_scaled = MagicMock()

        with patch('pgchess.gui.sprites.pygame.image.load', return_value=mock_surface):
            with patch('pgchess.gui.sprites.get_resource_path', side_effect=lambda p: p):
                with patch('pgchess.gui.sprites.pygame.transform.smoothscale', return_value=mock_scaled):
                    window = MagicMock(spec=pygame.Surface)
                    sprites = Sprites(window)

                    expected_codes = {'kl', 'kd', 'ql', 'qd', 'bl',
                                      'bd', 'nl', 'nd', 'rl', 'rd', 'pl', 'pd'}
                    assert set(sprites._sprites.keys()) == expected_codes


class TestScaleSprite:
    """Test the sprite scaling method."""

    def test_calls_smoothscale_with_floored_dimensions(self):
        """scale_sprite should floor the width/height before passing to smoothscale."""
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_scaled = MagicMock()

        with patch('pgchess.gui.sprites.pygame.image.load', return_value=mock_surface):
            with patch('pgchess.gui.sprites.get_resource_path', side_effect=lambda p: p):
                with patch('pgchess.gui.sprites.pygame.transform.smoothscale'):
                    window = MagicMock(spec=pygame.Surface)
                    sprites = Sprites(window)

        with patch('pgchess.gui.sprites.pygame.transform.smoothscale', return_value=mock_scaled) as mock_scale:
            result = sprites.scale_sprite(mock_surface, 82.5, 82.5)
            mock_scale.assert_called_once_with(mock_surface, (82, 82))
            assert result == mock_scaled

    def test_integer_dimensions_unchanged(self):
        """Integer dimensions should pass through without modification."""
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface

        with patch('pgchess.gui.sprites.pygame.image.load', return_value=mock_surface):
            with patch('pgchess.gui.sprites.get_resource_path', side_effect=lambda p: p):
                with patch('pgchess.gui.sprites.pygame.transform.smoothscale'):
                    window = MagicMock(spec=pygame.Surface)
                    sprites = Sprites(window)

        with patch('pgchess.gui.sprites.pygame.transform.smoothscale') as mock_scale:
            sprites.scale_sprite(mock_surface, 75, 75)
            mock_scale.assert_called_once_with(mock_surface, (75, 75))


class TestGetSpriteFromCode:
    """Test sprite lookup by piece code."""

    def _make_sprites(self):
        """Create a Sprites instance with mocked pygame calls."""
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface

        with patch('pgchess.gui.sprites.pygame.image.load', return_value=mock_surface):
            with patch('pgchess.gui.sprites.get_resource_path', side_effect=lambda p: p):
                with patch('pgchess.gui.sprites.pygame.transform.smoothscale', return_value=MagicMock()):
                    window = MagicMock(spec=pygame.Surface)
                    return Sprites(window)

    def test_returns_sprite_for_valid_code(self):
        """A known piece code should return a surface."""
        sprites = self._make_sprites()
        result = sprites.get_sprite_from_code('kl')
        assert result is not None

    def test_returns_none_for_unknown_code(self):
        """An unknown piece code should return None."""
        sprites = self._make_sprites()
        result = sprites.get_sprite_from_code('xx')
        assert result is None

    def test_returns_none_for_empty_string(self):
        """An empty piece code should return None."""
        sprites = self._make_sprites()
        result = sprites.get_sprite_from_code('')
        assert result is None

    def test_scales_when_dimensions_provided(self):
        """When width and height are given, the sprite should be scaled."""
        sprites = self._make_sprites()
        mock_scaled = MagicMock()

        with patch.object(sprites, 'scale_sprite', return_value=mock_scaled) as mock_scale:
            result = sprites.get_sprite_from_code('pl', 100, 100)
            mock_scale.assert_called_once()
            assert result == mock_scaled

    def test_no_scaling_without_dimensions(self):
        """Without width/height, the raw sprite should be returned."""
        sprites = self._make_sprites()

        with patch.object(sprites, 'scale_sprite') as mock_scale:
            sprites.get_sprite_from_code('pl')
            mock_scale.assert_not_called()

    def test_no_scaling_with_none_dimensions(self):
        """Explicitly passing None for width/height should skip scaling."""
        sprites = self._make_sprites()

        with patch.object(sprites, 'scale_sprite') as mock_scale:
            sprites.get_sprite_from_code('pl', None, None)
            mock_scale.assert_not_called()
