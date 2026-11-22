import { useEffect, useRef } from 'react';
import { Animated, Easing } from 'react-native';
import Svg, { Circle, Defs, Path, RadialGradient, Rect, Stop } from 'react-native-svg';

const AC = Animated.createAnimatedComponent(Circle);

function useBreath(from: number, to: number, duration: number) {
  const v = useRef(new Animated.Value(from)).current;
  useEffect(() => {
    Animated.loop(Animated.sequence([
      Animated.timing(v, { toValue: to, duration, easing: Easing.inOut(Easing.sin), useNativeDriver: false }),
      Animated.timing(v, { toValue: from, duration, easing: Easing.inOut(Easing.sin), useNativeDriver: false }),
    ])).start();
  }, []);
  return v;
}

// Yalnızca süs: gerçek konum göstermez. Parıltının rengi seçili bölgenin seviyesini yansıtır.
export default function MapArt({ color = '#8A8599' }: { color?: string }) {
  const r1 = useBreath(118, 134, 2600);
  return (
    <Svg width="100%" height="100%" viewBox="0 0 390 844" preserveAspectRatio="xMidYMid slice" style={{ position: 'absolute' }}>
      <Defs>
        <RadialGradient id="g" cx="50%" cy="50%" r="50%"><Stop offset="0" stopColor={color} stopOpacity="0.45" /><Stop offset="1" stopColor={color} stopOpacity="0" /></RadialGradient>
      </Defs>
      <Rect width="390" height="844" fill="#F6F1E7" />
      <Path d="M0 600 C90 560 150 650 230 670 C310 690 360 730 390 720 L390 844 L0 844 Z" fill="#CFE3E6" />
      <Rect x="255" y="170" width="115" height="85" rx="22" fill="#D5E4C8" />
      <Path d="M-10 290 L400 360 M-10 500 L400 450 M130 -10 L190 860 M300 -10 L255 860" stroke="#FFFFFF" strokeWidth="14" strokeLinecap="round" fill="none" />
      <Path d="M-10 190 L400 240 M-10 410 L400 540 M50 -10 L80 860 M355 -10 L335 860" stroke="#E9E0CD" strokeWidth="5" strokeLinecap="round" fill="none" />
      <AC cx="195" cy="360" r={r1} fill="url(#g)" />
    </Svg>
  );
}
