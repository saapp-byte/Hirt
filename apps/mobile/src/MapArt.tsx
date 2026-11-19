import { useEffect, useRef } from 'react';
import { Animated, Easing } from 'react-native';
import Svg, { Circle, Defs, Path, RadialGradient, Rect, Stop, Text as SvgText } from 'react-native-svg';

const AC = Animated.createAnimatedComponent(Circle);

// Yarıçapı yavaşça "nefes alan" değer
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

// Şimdilik çizilmiş harita. Gerçek harita (MapLibre) sonraki aşamada gelecek.
export default function MapArt() {
  const r1 = useBreath(118, 134, 2600);
  const r2 = useBreath(74, 88, 3200);
  const r3 = useBreath(14, 26, 1800);
  return (
    <Svg width="100%" height="100%" viewBox="0 0 390 844" preserveAspectRatio="xMidYMid slice" style={{ position: 'absolute' }}>
      <Defs>
        <RadialGradient id="c" cx="50%" cy="50%" r="50%"><Stop offset="0" stopColor="#F07B3F" stopOpacity="0.5" /><Stop offset="1" stopColor="#F07B3F" stopOpacity="0" /></RadialGradient>
        <RadialGradient id="t" cx="50%" cy="50%" r="50%"><Stop offset="0" stopColor="#2E9E8A" stopOpacity="0.35" /><Stop offset="1" stopColor="#2E9E8A" stopOpacity="0" /></RadialGradient>
      </Defs>
      <Rect width="390" height="844" fill="#F6F1E7" />
      <Path d="M0 600 C90 560 150 650 230 670 C310 690 360 730 390 720 L390 844 L0 844 Z" fill="#CFE3E6" />
      <Rect x="255" y="170" width="115" height="85" rx="22" fill="#D5E4C8" />
      <Path d="M-10 290 L400 360 M-10 500 L400 450 M130 -10 L190 860 M300 -10 L255 860" stroke="#FFFFFF" strokeWidth="14" strokeLinecap="round" fill="none" />
      <Path d="M-10 190 L400 240 M-10 410 L400 540 M50 -10 L80 860 M355 -10 L335 860" stroke="#E9E0CD" strokeWidth="5" strokeLinecap="round" fill="none" />
      <AC cx="150" cy="400" r={r1} fill="url(#c)" />
      <AC cx="290" cy="320" r={r2} fill="url(#c)" opacity="0.6" />
      <Circle cx="90" cy="230" r="90" fill="url(#t)" />
      <Circle cx="320" cy="500" r="80" fill="url(#t)" />
      <Circle cx="142" cy="392" r="9" fill="#F07B3F" stroke="#fff" strokeWidth="3" />
      <Circle cx="176" cy="420" r="7" fill="#F07B3F" stroke="#fff" strokeWidth="3" />
      <Circle cx="288" cy="324" r="8" fill="#F07B3F" stroke="#fff" strokeWidth="3" />
      <SvgText x="100" y="352" fontSize="13" fontWeight="600" fill="#5E5A6E">Moda Caddesi</SvgText>
      <SvgText x="268" y="215" fontSize="12" fontWeight="600" fill="#4E6B45">Park</SvgText>
      <SvgText x="20" y="740" fontSize="13" fontWeight="600" fill="#4B7A85">Deniz</SvgText>
      <SvgText x="40" y="262" fontSize="12" fontWeight="600" fill="#5E5A6E">Kadıköy</SvgText>
      <AC cx="215" cy="480" r={r3} fill="#2F5BFF" fillOpacity="0.2" />
      <Circle cx="215" cy="480" r="8" fill="#2F5BFF" stroke="#fff" strokeWidth="3" />
      <Rect x="232" y="468" width="92" height="24" rx="12" fill="#1D1B2E" />
      <SvgText x="278" y="484" fontSize="12" fontWeight="700" fill="#FFFFFF" textAnchor="middle">Sen buradasın</SvgText>
    </Svg>
  );
}
