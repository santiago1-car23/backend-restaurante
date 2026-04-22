import React, { memo, useEffect, useMemo, useRef } from 'react';
import {
  Animated,
  Dimensions,
  Easing,
  PanResponder,
  Pressable,
  StyleSheet,
  Text,
  TouchableOpacity,
  useWindowDimensions,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../../constants/colors';

type ActionItem = {
  key: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  color: string;
  onPress: () => void | Promise<void>;
};

type Props = {
  open: boolean;
  onToggle: () => void;
  actions: ActionItem[];
};

function FloatingActionDock({ open, onToggle, actions }: Props) {
  const progress = useRef(new Animated.Value(0)).current;
  const position = useRef(new Animated.ValueXY()).current;
  const hasPosition = useRef(false);
  const dragMoved = useRef(false);
  const { width, height } = useWindowDimensions();
  const getPositionValue = () => (position as any).__getValue() as { x: number; y: number };

  useEffect(() => {
    const triggerSize = 68;
    const marginRight = 22;
    const marginBottom = 26;
    const nextX = Math.max(width - triggerSize - marginRight, 12);
    const nextY = Math.max(height - triggerSize - marginBottom, 12);

    if (!hasPosition.current) {
      position.setValue({ x: nextX, y: nextY });
      hasPosition.current = true;
      return;
    }

    const current = getPositionValue();
    const clampedX = Math.min(Math.max(current.x, 12), Math.max(width - triggerSize - 12, 12));
    const clampedY = Math.min(Math.max(current.y, 12), Math.max(height - triggerSize - 12, 12));
    position.setValue({ x: clampedX, y: clampedY });
  }, [height, position, width]);

  useEffect(() => {
    Animated.timing(progress, {
      toValue: open ? 1 : 0,
      duration: 280,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  }, [open, progress]);

  const backdropOpacity = progress.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 1],
  });

  const rotate = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '45deg'],
  });

  const pulseScale = useMemo(
    () =>
      progress.interpolate({
        inputRange: [0, 1],
        outputRange: [1, 1.06],
      }),
    [progress]
  );

  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => false,
        onMoveShouldSetPanResponder: (_, gestureState) =>
          Math.abs(gestureState.dx) > 6 || Math.abs(gestureState.dy) > 6,
        onPanResponderGrant: () => {
          dragMoved.current = false;
          position.setOffset(getPositionValue());
          position.setValue({ x: 0, y: 0 });
        },
        onPanResponderMove: (_, gestureState) => {
          if (Math.abs(gestureState.dx) > 2 || Math.abs(gestureState.dy) > 2) {
            dragMoved.current = true;
          }
          position.setValue({ x: gestureState.dx, y: gestureState.dy });
        },
        onPanResponderRelease: () => {
          position.flattenOffset();
          const triggerSize = 68;
          const current = getPositionValue();
          const clampedX = Math.min(Math.max(current.x, 12), Math.max(width - triggerSize - 12, 12));
          const clampedY = Math.min(Math.max(current.y, 12), Math.max(height - triggerSize - 12, 12));
          Animated.spring(position, {
            toValue: { x: clampedX, y: clampedY },
            useNativeDriver: false,
            bounciness: 6,
          }).start();
        },
        onPanResponderTerminate: () => {
          position.flattenOffset();
          dragMoved.current = false;
        },
      }),
    [height, position, width]
  );

  const handleTriggerPress = () => {
    if (dragMoved.current) {
      dragMoved.current = false;
      return;
    }
    onToggle();
  };

  return (
    <>
      <Animated.View
        pointerEvents={open ? 'auto' : 'none'}
        style={[styles.overlay, { opacity: backdropOpacity }]}
      >
        <Pressable style={StyleSheet.absoluteFill} onPress={onToggle} />
      </Animated.View>

      <Animated.View
        pointerEvents="box-none"
        style={[styles.root, { transform: position.getTranslateTransform() }]}
      >
        <View style={styles.actionsWrap} pointerEvents="box-none">
          {actions.map((action, index) => {
            const offset = (index + 1) * 78;
            const translateY = progress.interpolate({
              inputRange: [0, 1],
              outputRange: [26, -offset],
            });
            const scale = progress.interpolate({
              inputRange: [0, 1],
              outputRange: [0.7, 1],
            });
            const opacity = progress.interpolate({
              inputRange: [0, 1],
              outputRange: [0, 1],
            });

            return (
              <Animated.View
                key={action.key}
                pointerEvents={open ? 'auto' : 'none'}
                style={[
                  styles.actionItem,
                  {
                    opacity,
                    transform: [{ translateY }, { scale }],
                  },
                ]}
              >
                <TouchableOpacity
                  activeOpacity={0.9}
                  onPress={action.onPress}
                  style={[styles.actionButton, { shadowColor: action.color }]}
                >
                  <View style={[styles.actionOrb, { backgroundColor: action.color }]}>
                    <Ionicons name={action.icon} size={20} color={colors.textMainDark} />
                  </View>
                  <View style={styles.labelWrap}>
                    <Text style={styles.actionLabel}>{action.label}</Text>
                  </View>
                </TouchableOpacity>
              </Animated.View>
            );
          })}
        </View>

        <Animated.View style={[styles.triggerGlow, { transform: [{ scale: pulseScale }] }]} />
        <Animated.View {...panResponder.panHandlers}>
          <TouchableOpacity
            activeOpacity={0.92}
            onPress={handleTriggerPress}
            style={styles.triggerButton}
          >
            <View style={styles.triggerCore}>
              <Animated.View style={{ transform: [{ rotate }] }}>
                <Ionicons name="add" size={30} color={colors.textIce} />
              </Animated.View>
            </View>
            <View style={styles.triggerSpec} />
          </TouchableOpacity>
        </Animated.View>
      </Animated.View>
    </>
  );
}

export default memo(FloatingActionDock);

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: colors.overlayBackdrop,
  },
  root: {
    position: 'absolute',
    left: 0,
    top: 0,
    alignItems: 'flex-end',
  },
  actionsWrap: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    alignItems: 'flex-end',
  },
  actionItem: {
    position: 'absolute',
    right: 4,
    bottom: 4,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 16,
    elevation: 10,
  },
  actionOrb: {
    width: 52,
    height: 52,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.overlayLightBorder,
  },
  labelWrap: {
    backgroundColor: colors.overlayDarkCard,
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.dockLabelBorder,
  },
  actionLabel: {
    color: colors.textMainDark,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
  triggerGlow: {
    position: 'absolute',
    width: 84,
    height: 84,
    borderRadius: 42,
    backgroundColor: colors.dockGlow,
    right: -8,
    bottom: -8,
  },
  triggerButton: {
    width: 68,
    height: 68,
    borderRadius: 28,
    backgroundColor: colors.bgBodyDark,
    padding: 5,
    shadowColor: colors.shadowDock,
    shadowOpacity: 0.34,
    shadowOffset: { width: 0, height: 16 },
    shadowRadius: 18,
    elevation: 16,
  },
  triggerCore: {
    flex: 1,
    borderRadius: 23,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.textSlate,
    borderWidth: 1,
    borderColor: colors.dockBorder,
  },
  triggerSpec: {
    position: 'absolute',
    top: 10,
    left: 12,
    width: 24,
    height: 8,
    borderRadius: 999,
    backgroundColor: colors.dockSpec,
  },
});
