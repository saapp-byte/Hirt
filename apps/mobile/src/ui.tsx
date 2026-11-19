import { ReactNode, useEffect, useRef } from 'react';
import { Animated, Easing, Pressable, StyleProp, View, ViewStyle } from 'react-native';
import { C } from './theme';

// Açılışta yumuşakça belirir (ve hafifçe yukarı kayar)
export function FadeIn({ children, delay = 0, rise = 14, style }: { children: ReactNode; delay?: number; rise?: number; style?: StyleProp<ViewStyle> }) {
  const v = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(v, { toValue: 1, duration: 380, delay, easing: Easing.out(Easing.cubic), useNativeDriver: true }).start();
  }, []);
  return (
    <Animated.View style={[style, { opacity: v, transform: [{ translateY: v.interpolate({ inputRange: [0, 1], outputRange: [rise, 0] }) }] }]}>
      {children}
    </Animated.View>
  );
}

// Basınca hafifçe küçülen düğme
export function PressScale({ children, style, onPress, accessibilityLabel }: { children: ReactNode; style?: StyleProp<ViewStyle>; onPress?: () => void; accessibilityLabel?: string }) {
  const sc = useRef(new Animated.Value(1)).current;
  const to = (n: number) => Animated.spring(sc, { toValue: n, useNativeDriver: true, speed: 40, bounciness: 0 }).start();
  return (
    <Pressable onPress={onPress} onPressIn={() => to(0.96)} onPressOut={() => to(1)} accessibilityLabel={accessibilityLabel}>
      <Animated.View style={[style, { transform: [{ scale: sc }] }]}>{children}</Animated.View>
    </Pressable>
  );
}

// Nabız gibi yayılan halkalar
export function PulseRings({ size = 230 }: { size?: number }) {
  return (
    <>
      {[0, 800, 1600].map((d) => <Ring key={d} delay={d} size={size} />)}
    </>
  );
}

function Ring({ delay, size }: { delay: number; size: number }) {
  const v = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.delay(delay),
        Animated.timing(v, { toValue: 1, duration: 2400, easing: Easing.out(Easing.quad), useNativeDriver: true }),
      ])
    ).start();
  }, []);
  return (
    <Animated.View
      pointerEvents="none"
      style={{
        position: 'absolute', width: size, height: size, borderRadius: size / 2, borderWidth: 3, borderColor: C.coral,
        opacity: v.interpolate({ inputRange: [0, 0.2, 1], outputRange: [0, 0.5, 0] }),
        transform: [{ scale: v.interpolate({ inputRange: [0, 1], outputRange: [0.5, 1.4] }) }],
      }}
    />
  );
}
