from unittest.mock import MagicMock, patch
import pytest
from gns3.qt import QtCore, QtWidgets
from test_group_item import canvas, drawing, device


@pytest.mark.parametrize('fail', [False, True])
def test_large_svg_streams_before_small_drawing_request_and_cleans_temp(canvas, fail):
    from unittest.mock import MagicMock
    from gns3.items.image_item import ImageItem
    project = MagicMock()
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="20"><metadata>' + 'x' * 1100000 + '</metadata><rect width="40" height="20"/></svg>'
    image = ImageItem(svg=svg, project=project)
    image.create()
    assert project.post.call_args.args[0] == '/drawings'
    project.post.call_args.args[1]({})  # Server initializes its image directory.
    path, callback = project.post.call_args.args
    temporary = project.post.call_args.kwargs['body']
    assert path.startswith('/files/project-files/images/') and temporary.exists()
    callback({'message': 'failed'} if fail else {}, error=fail)
    assert not temporary.exists()
    if fail:
        assert project.post.call_count == 2 and not image._create_pending
    else:
        assert project.post.call_args.args[0] == '/drawings'
        body = project.post.call_args.kwargs['body']
        assert body['svg'].endswith('.svg') and len(body['svg']) < 100
