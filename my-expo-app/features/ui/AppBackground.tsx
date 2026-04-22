import React, { memo } from 'react';
import { StyleSheet, View } from 'react-native';

const colors = {
  primary: '#00A6CC',
  darkBlue: '#0A5A86',
  surfaceCard: '#FFFFFF',
  gridLine: 'rgba(255, 255, 255, 0.24)',
} as const;

const gridIndexes = Array.from({ length: 24 }, (_, i) => i);

const GridLines = memo(function GridLines({ prefix }: { prefix: string }) {
  return (
    <View style={styles.gridContainer}>
      {gridIndexes.map((i) => (
        <View
          key={`${prefix}-line-a-${i}`}
          style={[
            styles.gridLine,
            {
              left: i * 30 - 100,
              transform: [{ rotate: '45deg' }],
            },
          ]}
        />
      ))}
      {gridIndexes.map((i) => (
        <View
          key={`${prefix}-line-b-${i}`}
          style={[
            styles.gridLine,
            {
              left: i * 30 - 100,
              transform: [{ rotate: '-45deg' }],
            },
          ]}
        />
      ))}
    </View>
  );
});

function AppBackground() {
  return (
    <View pointerEvents="none" style={styles.root}>
      <View style={styles.topContainer}>
        <View style={styles.shapeBase}>
          <GridLines prefix="top" />
        </View>
        <View style={styles.cyanCurveTop} />
        <View style={styles.whiteMaskTop} />
        <View style={styles.whiteStrokeTop} />
      </View>

      <View style={styles.bottomContainer}>
        <View style={styles.shapeBase}>
          <GridLines prefix="bottom" />
        </View>
        <View style={styles.cyanCurveBottom} />
        <View style={styles.whiteMaskBottom} />
        <View style={styles.whiteStrokeBottom} />
      </View>
    </View>
  );
}

export default memo(AppBackground);

const styles = StyleSheet.create({
  root: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: colors.surfaceCard,
    overflow: 'hidden',
  },
  topContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '16%',
    overflow: 'hidden',
  },
  bottomContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '16%',
    overflow: 'hidden',
  },
  shapeBase: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: colors.darkBlue,
  },
  gridContainer: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.65,
  },
  gridLine: {
    position: 'absolute',
    width: 1,
    height: 1000,
    top: -400,
    backgroundColor: colors.gridLine,
  },
  cyanCurveTop: {
    position: 'absolute',
    width: '126%',
    height: '160%',
    borderRadius: 9999,
    backgroundColor: colors.primary,
    bottom: '-100%',
    left: '-13%',
  },
  whiteMaskTop: {
    position: 'absolute',
    width: '145%',
    height: '190%',
    borderRadius: 9999,
    backgroundColor: colors.surfaceCard,
    bottom: '-144%',
    left: '-22%',
  },
  cyanCurveBottom: {
    position: 'absolute',
    width: '126%',
    height: '160%',
    borderRadius: 9999,
    backgroundColor: colors.primary,
    top: '-100%',
    left: '-13%',
  },
  whiteMaskBottom: {
    position: 'absolute',
    width: '145%',
    height: '190%',
    borderRadius: 9999,
    backgroundColor: colors.surfaceCard,
    top: '-144%',
    left: '-22%',
  },
  whiteStrokeTop: {
    position: 'absolute',
    width: '124%',
    height: '148%',
    borderRadius: 9999,
    borderWidth: 4,
    borderColor: colors.surfaceCard,
    backgroundColor: 'transparent',
    bottom: '-106%',
    left: '-11%',
    opacity: 1,
  },
  whiteStrokeBottom: {
    position: 'absolute',
    width: '124%',
    height: '148%',
    borderRadius: 9999,
    borderWidth: 4,
    borderColor: colors.surfaceCard,
    backgroundColor: 'transparent',
    top: '-106%',
    left: '-11%',
    opacity: 1,
  },
});
