"""Tests for pychess.gui.sounds: sound effect playback routing."""
from unittest.mock import patch, MagicMock

from pgchess import constants
from pgchess.gui.sounds import Sounds


class TestSoundsPlay:
    """Test the internal _play helper and individual sound methods."""

    def test_play_loads_and_plays_sound(self):
        """_play should load the resolved path and call .play() on the Sound."""
        sounds = Sounds()
        mock_sound_instance = MagicMock()

        with patch('pychess.gui.sounds.pygame.mixer.Sound', return_value=mock_sound_instance) as mock_sound:
            with patch('pychess.gui.sounds.get_resource_path', return_value='/resolved/path.wav') as mock_path:
                sounds._play('assets/sounds/test.wav')
                mock_path.assert_called_once_with('assets/sounds/test.wav')
                mock_sound.assert_called_once_with('/resolved/path.wav')
                mock_sound_instance.play.assert_called_once()

    def test_play_game_start(self):
        """play_game_start should play the game start sound."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_game_start()
            mock_play.assert_called_once_with(constants.PATH_GAME_START)

    def test_play_game_over(self):
        """play_game_over should play the game over sound."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_game_over()
            mock_play.assert_called_once_with(constants.PATH_GAME_OVER)

    def test_play_error(self):
        """play_error should play the error sound."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_error()
            mock_play.assert_called_once_with(constants.PATH_ERROR)

    def test_play_piece_capture(self):
        """play_piece_capture should play the capture sound."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_piece_capture()
            mock_play.assert_called_once_with(constants.PATH_PIECE_CAPTURE)

    def test_play_piece_check(self):
        """play_piece_check should play the check sound."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_piece_check()
            mock_play.assert_called_once_with(constants.PATH_PIECE_CHECK)


class TestPlayPieceMove:
    """Test the play_piece_move routing logic."""

    def test_normal_light_move(self):
        """A non-capture light move should play PATH_PIECE_MOVE."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_piece_move(is_capture=False, is_dark=False)
            mock_play.assert_called_once_with(constants.PATH_PIECE_MOVE)

    def test_normal_dark_move(self):
        """A non-capture dark move should play PATH_PIECE_MOVE_2."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_piece_move(is_capture=False, is_dark=True)
            mock_play.assert_called_once_with(constants.PATH_PIECE_MOVE_2)

    def test_capture_plays_capture_sound(self):
        """A capture should play the capture sound regardless of color."""
        sounds = Sounds()
        with patch.object(sounds, 'play_piece_capture') as mock_capture:
            sounds.play_piece_move(is_capture=True, is_dark=False)
            mock_capture.assert_called_once()

    def test_capture_dark_still_plays_capture(self):
        """A dark capture should still play the capture sound, not the dark move sound."""
        sounds = Sounds()
        with patch.object(sounds, 'play_piece_capture') as mock_capture:
            with patch.object(sounds, '_play') as mock_play:
                sounds.play_piece_move(is_capture=True, is_dark=True)
                mock_capture.assert_called_once()
                mock_play.assert_not_called()

    def test_default_args(self):
        """Calling with no args should play the light non-capture sound."""
        sounds = Sounds()
        with patch.object(sounds, '_play') as mock_play:
            sounds.play_piece_move()
            mock_play.assert_called_once_with(constants.PATH_PIECE_MOVE)
