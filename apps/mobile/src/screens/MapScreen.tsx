import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Alert, Animated, Easing, Pressable, StyleSheet, Text, View } from 'react-native';
import MapArt from '../MapArt';
import { Summary, adviceTr, levelColor, levelSegments } from '../api';
import { C } from '../theme';
import { FadeIn, PressScale } from '../ui';

type Props = { summary: Summary | null; onOpen: () => void; hintOpen: boolean; onCloseHint: () => void };

export default function MapScreen({ summary, onOpen, hintOpen, onCloseHint }: Props) {
  const [when, setWhen] = useState('Bu gece');
  const slide = useRef(new Animated.Value(320)).current;
  useEffect(() => {
    Animated.timing(slide, { toValue: 0, duration: 520, delay: 150, easing: Easing.out(Easing.cubic), useNativeDriver: true }).start();
  }, []);
  const color = summary ? levelColor(summary.level) : C.ink;
  const segs = summary ? levelSegments(summary.level) : 0;
  return (
    <View style={{ flex: 1, backgroundColor: C.bg }}>
      <MapArt />
      <View style={s.top}>
        <Pressable style={s.search} onPress={() => Alert.alert('Yakında', 'Yer arama sonraki sürümde.')} accessibilityLabel="Yer ara">
          <Text style={s.searchText}>Yer ara (yakında)</Text>
        </Pressable>
        <View style={{ flexDirection: 'row', gap: 8 }}>
          {['Şimdi', 'Bu gece', 'Hafta sonu'].map((t) => (
            <PressScale key={t} onPress={() => setWhen(t)} style={[s.chip, when === t && s.chipOn]}>
              <Text style={[s.chipText, when === t && { color: C.bg }]}>{t}</Text>
            </PressScale>
          ))}
        </View>
        {hintOpen && (
          <FadeIn style={s.hint} delay={700}>
            <Text style={s.hintText}>Turuncu alanlar, son haftalarda olay bildirilen yerleri gösterir. Aşağıdaki kart bulunduğun bölgeyi özetler.</Text>
            <PressScale onPress={onCloseHint} style={s.hintBtn}><Text style={s.hintBtnText}>Anladım</Text></PressScale>
          </FadeIn>
        )}
      </View>

      <Animated.View style={[s.sheet, { transform: [{ translateY: slide }] }]}>
        <View style={s.handle} />
        {!summary ? <ActivityIndicator color={C.ink} style={{ margin: 40 }} /> : (
          <>
            <Text style={s.place}>{summary.name}, {summary.district}</Text>
            <View style={[s.pill, { backgroundColor: color }]}>
              <Text style={s.pillText}>{when}: {summary.level}</Text>
            </View>
            <View style={{ flexDirection: 'row', gap: 6 }}>
              {[1, 2, 3, 4, 5].map((i) => <FadeIn key={i} rise={0} delay={500 + i * 90} style={{ flex: 1 }}><View style={[s.seg, i <= segs && { backgroundColor: color }]} /></FadeIn>)}
            </View>
            <Text style={s.body}>{adviceTr(summary.level)}</Text>
            {summary.sample_data && <Text style={s.tag}>ÖRNEK VERİ</Text>}
            <PressScale style={s.btn} onPress={onOpen}><Text style={s.btnText}>Nedenini ve detayları gör</Text></PressScale>
          </>
        )}
      </Animated.View>
    </View>
  );
}

const s = StyleSheet.create({
  top: { position: 'absolute', top: 48, left: 16, right: 16, gap: 10 },
  search: { height: 54, borderRadius: 27, backgroundColor: C.card, borderWidth: 1, borderColor: C.line, paddingHorizontal: 20, justifyContent: 'center', elevation: 4 },
  searchText: { fontSize: 16, color: C.sub },
  chip: { minHeight: 44, paddingHorizontal: 18, borderRadius: 22, backgroundColor: C.card, borderWidth: 1, borderColor: C.line, justifyContent: 'center' },
  chipOn: { backgroundColor: C.ink, borderColor: C.ink },
  chipText: { fontSize: 15, fontWeight: '600', color: C.ink },
  hint: { backgroundColor: C.ink, borderRadius: 18, padding: 16, gap: 10, elevation: 6 },
  hintText: { color: C.bg, fontSize: 15, lineHeight: 22 },
  hintBtn: { alignSelf: 'flex-end', minHeight: 40, paddingHorizontal: 16, borderRadius: 20, backgroundColor: C.bg, justifyContent: 'center' },
  hintBtnText: { color: C.ink, fontWeight: '700', fontSize: 14 },
  sheet: { position: 'absolute', left: 0, right: 0, bottom: 0, backgroundColor: C.card, borderTopLeftRadius: 32, borderTopRightRadius: 32, padding: 24, paddingTop: 14, gap: 12, elevation: 12 },
  handle: { width: 40, height: 4, borderRadius: 2, backgroundColor: '#DDD2BC', alignSelf: 'center' },
  place: { fontSize: 24, fontWeight: '700', color: C.ink },
  pill: { alignSelf: 'flex-start', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 18 },
  pillText: { color: '#FFFFFF', fontSize: 15, fontWeight: '700' },
  seg: { flex: 1, height: 8, borderRadius: 4, backgroundColor: C.track },
  body: { fontSize: 16, lineHeight: 24, color: C.body },
  tag: { alignSelf: 'flex-start', fontSize: 11, fontWeight: '600', color: C.sub, backgroundColor: '#F1E9D8', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 10, overflow: 'hidden' },
  btn: { minHeight: 54, borderRadius: 27, backgroundColor: C.ink, alignItems: 'center', justifyContent: 'center', marginTop: 4 },
  btnText: { color: C.bg, fontSize: 16, fontWeight: '600' },
});
