# coding:utf-8
from typing import Union

from PySide6.QtCore import Qt, QRectF, QSize, QPoint, Property, QEvent
from PySide6.QtGui import QPainterPath, QIcon, QPainter, QColor, QPen
from PySide6.QtWidgets import QPushButton, QToolButton, QApplication, QWidget

from ...common.color import translucent, mixColor
from ...common.icon import MaterialIconBase, drawIcon, isDarkTheme, Theme, toQIcon, Icon
from ...common.font import setFont
from ...common.style_sheet import (MaterialStyleSheet, themeColor, ThemeColor, palette,
                                   hoverMixPrimary, pressedMixPrimary)
from ...common.animation import BackgroundAnimationWidget, DropShadowAnimation
from ...common.overload import singledispatchmethod
from .ripple import RippleOverlayWidget, RippleStyle



class PushButton(BackgroundAnimationWidget, QPushButton):
    """ push button """

    @singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        MaterialStyleSheet.BUTTON.apply(self)
        self.rippleWidget = RippleOverlayWidget(self)

        self.rippleStyle = RippleStyle.POSITIONED
        self._iconPadding = 18

        self.setBorderRadius(-1)
        self.setIconSize(QSize(16, 16))
        self.setIcon(None)
        setFont(self)

        self._postInit()

    @__init__.register
    def _(self, text: str, parent: QWidget = None, icon: Union[QIcon, str, MaterialIconBase] = None):
        self.__init__(parent=parent)
        self.setText(text)
        self.setIcon(icon)

    def _postInit(self):
        pass

    def setIcon(self, icon: Union[QIcon, str, MaterialIconBase]):
        self.setProperty('hasIcon', icon is not None)
        self.setStyle(QApplication.style())
        self._icon = icon or QIcon()
        self.update()

    def icon(self):
        return toQIcon(self._icon)

    def setProperty(self, name: str, value) -> bool:
        if name != 'icon':
            return super().setProperty(name, value)

        self.setIcon(value)
        return True

    def setRippleStyle(self, style: RippleStyle):
        self.rippleWidget.setRippleStyle(style)

    def _drawIcon(self, icon, painter, rect, state=QIcon.State.Off):
        """ draw icon """
        drawIcon(icon, painter, rect, state)

    def _drawBackground(self, painter: QPainter):
        painter.setBrush(self.backgroundColor)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, self.borderRadius, self.borderRadius)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.PenStyle.NoPen)

        # draw background
        painter.save()
        self._drawBackground(painter)
        painter.restore()
        painter.end()

        super().paintEvent(e)

        if self.icon().isNull():
            return

        painter.begin(self)
        if not self.isEnabled():
            painter.setOpacity(0.3628)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        mw = self.minimumSizeHint().width()
        if mw > 0:
            self._drawIcon(self._icon, painter, QRectF(
                self._iconPadding + (self.width()-mw)//2, y, w, h))
        else:
            self._drawIcon(self._icon, painter, QRectF(self._iconPadding, y, w, h))

    def resizeEvent(self, e):
        self._updateRippleClipPath()

    def _updateRippleClipPath(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.borderRadius, self.borderRadius)
        self.rippleWidget.setClipPath(path)

    def getBorderRadius(self):
        return self._borderRadius if self._borderRadius >= 0 else self.height() / 2

    def setBorderRadius(self, radius: int):
        """ set border radius, -1 represents full rounded corners """
        self._borderRadius = radius
        self._updateRippleClipPath()
        self.update()

    borderRadius = Property(int, getBorderRadius, setBorderRadius)



class FilledPushButton(PushButton):
    """ Filled push button """

    def _postInit(self):
        self.shadowAni = DropShadowAnimation(self)
        self.shadowAni.setBlurRadius(15)
        self.shadowAni.setOffset(0, 2)

    def _normalBackgroundColor(self):
        return themeColor()

    def _hoverBackgroundColor(self):
        return mixColor(palette.onPrimary, self._normalBackgroundColor(), 0.08)

    def _pressedBackgroundColor(self):
        return mixColor(palette.onPrimary, self._normalBackgroundColor(), 0.12)

    def _disabledBackgroundColor(self):
        return QColor(230, 224, 233, 31) if isDarkTheme() else QColor(29, 27, 32, 31)

    def _drawIcon(self, icon, painter, rect, state=QIcon.State.Off):
        if isinstance(icon, MaterialIconBase) and self.isEnabled():
            theme = Theme.DARK if not isDarkTheme() else Theme.LIGHT
            icon = icon.icon(theme)
        elif not self.isEnabled():
            painter.setOpacity(0.38)

        drawIcon(icon, painter, rect, state)


class OutlinedPushButton(PushButton):
    """ Outlined push button """

    def _drawIcon(self, icon, painter, rect, state=QIcon.State.Off):
        """ draw icon """
        if isinstance(icon, MaterialIconBase) and self.isEnabled():
            icon = icon.icon(color=themeColor())

        drawIcon(icon, painter, rect, state)

    def _hoverBackgroundColor(self):
        return translucent(themeColor(), 20)

    def _pressedBackgroundColor(self):
        return translucent(themeColor(), 30)

    def _drawBackground(self, painter: QPainter):
        isDark = isDarkTheme()

        if not self.isEnabled():
            painter.setPen(QColor(230, 224, 233, 31) if isDark else QColor(29, 27, 32, 31))
        else:
            painter.setPen(palette.outline)

        super()._drawBackground(painter)


class TextPushButton(OutlinedPushButton):
    """ Text push button """

    def _postInit(self):
        self._iconPadding = 14

    def _drawBackground(self, painter: QPainter):
        PushButton._drawBackground(self, painter)


class ElevatedPushButton(FilledPushButton):
    """ Elevated push button """

    def _normalBackgroundColor(self):
        return palette.surfaceContainerLow

    def _hoverBackgroundColor(self):
        return hoverMixPrimary(self._normalBackgroundColor())

    def _pressedBackgroundColor(self):
        return pressedMixPrimary(self._normalBackgroundColor())

    def _postInit(self):
        super()._postInit()
        self.shadowAni.setNormalColor(QColor(0, 0, 0, 75))

    def _drawIcon(self, icon, painter, rect, state=QIcon.State.Off):
        return OutlinedPushButton._drawIcon(self, icon, painter, rect, state)

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() == QEvent.Type.EnabledChange:
                a = 75 if self.isEnabled() else 0
                self.shadowAni.setColor(QColor(0, 0, 0, a))

        return PushButton.eventFilter(self, obj, e)


class TonalPushButton(FilledPushButton):
    """ Tonal push button """

    def _normalBackgroundColor(self):
        return palette.secondaryContainer

    def _hoverBackgroundColor(self):
        return mixColor(palette.onSecondaryContainer, self._normalBackgroundColor(), 0.08)

    def _pressedBackgroundColor(self):
        return mixColor(palette.onSecondaryContainer, self._normalBackgroundColor(), 0.12)

    def _drawIcon(self, icon, painter, rect, state=QIcon.State.Off):
        return drawIcon(icon, painter, rect, state)



class ToolButton(BackgroundAnimationWidget, QToolButton):
    """ Tool button """

    @singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.rippleWidget = RippleOverlayWidget(self)
        self.rippleStyle = RippleStyle.POSITIONED

        self.setBorderRadius(-1)
        self.installEventFilter(self)
        self.setIconSize(QSize(16, 16))
        self.setFixedSize(36, 36)
        self.setIcon(QIcon())
        setFont(self)
        self.toggled.connect(self._updateBackgroundColor)

        self._postInit()

    @__init__.register
    def _(self, icon: MaterialIconBase, parent: QWidget = None):
        self.__init__(parent)
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: QIcon, parent: QWidget = None):
        self.__init__(parent)
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: str, parent: QWidget = None):
        self.__init__(parent)
        self.setIcon(icon)

    def _postInit(self):
        pass

    def setIcon(self, icon: Union[QIcon, str, MaterialIconBase]):
        self._icon = icon
        self.update()

    def icon(self):
        return toQIcon(self._icon)

    def setProperty(self, name: str, value) -> bool:
        if name != 'icon':
            return super().setProperty(name, value)

        self.setIcon(value)
        return True

    def setRippleStyle(self, style: RippleStyle):
        self.rippleWidget.setRippleStyle(style)

    def _normalBackgroundColor(self):
        return QColor(0, 0, 0, 0)

    def _hoverBackgroundColor(self):
        return QColor(0, 0, 0, 0)

    def _pressedBackgroundColor(self):
        return QColor(0, 0, 0, 0)

    def _disabledBackgroundColor(self):
        return QColor(0, 0, 0, 0)

    def resizeEvent(self, e):
        self._updateRippleClipPath()

    def _updateRippleClipPath(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.borderRadius, self.borderRadius)
        self.rippleWidget.setClipPath(path)

    def _drawIcon(self, icon, painter: QPainter, rect: QRectF, state=QIcon.State.Off):
        """ draw icon """
        drawIcon(icon, painter, rect, state)

    def _drawBackground(self, painter: QPainter):
        painter.setBrush(self.backgroundColor)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, self.borderRadius, self.borderRadius)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)

        # draw background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.save()
        self._drawBackground(painter)
        painter.restore()

        if not self.isEnabled():
            painter.setOpacity(0.43)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        x = (self.width() - w) / 2
        self._drawIcon(self._icon, painter, QRectF(x, y, w, h))

    def getBorderRadius(self):
        return self._borderRadius if self._borderRadius >= 0 else self.height() / 2

    def setBorderRadius(self, radius: int):
        """ set border radius, -1 represents full rounded corners """
        self._borderRadius = radius
        self._updateRippleClipPath()
        self.update()

    borderRadius = Property(int, getBorderRadius, setBorderRadius)


class TransparentToolButton(ToolButton):
    """ Tranparent tool button """

    def _hoverBackgroundColor(self):
        return translucent(palette.onSurfaceVariant, 20)

    def _pressedBackgroundColor(self):
        return translucent(palette.onSurfaceVariant, 30)


class FilledToolButton(ToolButton):
    """ Filled tool button """

    def _normalBackgroundColor(self):
        return themeColor()

    def _hoverBackgroundColor(self):
        return mixColor(palette.onPrimary, self._normalBackgroundColor(), 0.08)

    def _pressedBackgroundColor(self):
        return mixColor(palette.onPrimary, self._normalBackgroundColor(), 0.12)

    def _disabledBackgroundColor(self):
        return QColor(230, 224, 233, 31) if isDarkTheme() else QColor(29, 27, 32, 31)

    def _drawIcon(self, icon, painter, rect, state=QIcon.State.Off):
        if isinstance(icon, MaterialIconBase) and self.isEnabled():
            theme = Theme.DARK if not isDarkTheme() else Theme.LIGHT
            icon = icon.icon(theme)
        elif not self.isEnabled():
            painter.setOpacity(0.38)

        drawIcon(icon, painter, rect, state)


class TonalToolButton(ToolButton):
    """ Tonal tool button """

    def _normalBackgroundColor(self):
        return palette.secondaryContainer

    def _hoverBackgroundColor(self):
        return mixColor(palette.onSecondaryContainer, self._normalBackgroundColor(), 0.08)

    def _pressedBackgroundColor(self):
        return mixColor(palette.onSecondaryContainer, self._normalBackgroundColor(), 0.12)


class OutlinedToolButton(TransparentToolButton):
    """ Outlined tool button """

    def _drawBackground(self, painter: QPainter):
        isDark = isDarkTheme()

        if not self.isEnabled():
            painter.setPen(QColor(230, 224, 233, 31) if isDark else QColor(29, 27, 32, 31))
        else:
            painter.setPen(palette.outline)

        super()._drawBackground(painter)


class TransparentToggleToolButton(TransparentToolButton):
    """ Transparent toggle tool button """

    def _postInit(self):
        self.setCheckable(True)

    def _hoverBackgroundColor(self):
        return translucent(themeColor(), 20) if self.isChecked() else super()._hoverBackgroundColor()

    def _pressedBackgroundColor(self):
        return translucent(themeColor(), 30) if self.isChecked() else super()._pressedBackgroundColor()

    def _drawIcon(self, icon, painter: QPainter, rect: QRectF, state=QIcon.State.Off):
        if not self.isChecked():
            return super()._drawIcon(icon, painter, rect, state)

        if not self.isEnabled():
            painter.setOpacity(0.38)
            drawIcon(icon, painter, rect, QIcon.State.On)
        else:
            drawIcon(icon, painter, rect, QIcon.State.On, fill=themeColor().name())


class FilledToggleToolButton(FilledToolButton):
    """ Filled toggle tool button """

    def _postInit(self):
        self.setCheckable(True)

    def _normalBackgroundColor(self):
        return super()._normalBackgroundColor() if self.isChecked() else translucent(themeColor(), 15)

    def _hoverBackgroundColor(self):
        return super()._hoverBackgroundColor() if self.isChecked() else translucent(themeColor(), 20)

    def _pressedBackgroundColor(self):
        return super()._pressedBackgroundColor() if self.isChecked() else translucent(themeColor(), 30)

    def _drawIcon(self, icon, painter: QPainter, rect: QRectF, state=QIcon.State.Off):
        if self.isChecked():
            return super()._drawIcon(icon, painter, rect, state)

        if not self.isEnabled():
            painter.setOpacity(0.38)
            drawIcon(icon, painter, rect, QIcon.State.On)
        else:
            drawIcon(icon, painter, rect, QIcon.State.On, fill=themeColor().name())


class OutlinedToggleToolButton(OutlinedToolButton):
    """ Outlined toggle tool button """

    def _postInit(self):
        self.setCheckable(True)

    def _normalBackgroundColor(self):
        return palette.inverseSurface if self.isChecked() else super()._normalBackgroundColor()

    def _hoverBackgroundColor(self):
        if not self.isChecked():
            return super()._hoverBackgroundColor()

        return mixColor(palette.inverseOnSurface, palette.inverseSurface, 0.08)

    def _pressedBackgroundColor(self):
        if not self.isChecked():
            return super()._pressedBackgroundColor()

        return mixColor(palette.inverseOnSurface, palette.inverseSurface, 0.12)

    def _disabledBackgroundColor(self):
        return QColor(230, 224, 233, 31) if isDarkTheme() else QColor(29, 27, 32, 31)

    def _drawIcon(self, icon, painter: QPainter, rect: QRectF, state=QIcon.State.Off):
        if not self.isChecked():
            return super()._drawIcon(icon, painter, rect, state)

        if isinstance(icon, MaterialIconBase) and self.isEnabled():
            theme = Theme.DARK if not isDarkTheme() else Theme.LIGHT
            icon = icon.icon(theme)
        elif not self.isEnabled():
            painter.setOpacity(0.38)

        drawIcon(icon, painter, rect, state)

    def _drawBackground(self, painter: QPainter):
        if self.isEnabled():
            painter.setPen('#938F99' if isDarkTheme() else '#79747E')

        ToolButton._drawBackground(self, painter)
