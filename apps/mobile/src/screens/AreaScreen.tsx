import { useEffect, useRef } from 'react';
import { Alert, Animated, Easing, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { KIND_TR, Summary, adviceTr, agoTr, confidenceTr } from '../api';
import { C } from '../theme';

const LABELS = ['06', '10', '16', '20', '00', '03'];

function Bar({ pct, on, delay }: { pct: number; on: boolean; delay: number }) {
  const v = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(v, { toValue: pct, duration: 600, delay, easing: Easing.out(Easing.cubic), useNativeDriver: false }).start();
  }, []);
  return (
    <View style={{ flex: 1, justifyContent: 'flex-end' }}>
      <Animated.View style={{ width: '100%', height: v.interpolate({ inputRange: [0, 100], outputRange: ['0%', '100%'] }), borderRadius: 6, backgroundColor: on ? C.coral : C.tealSoft }} />
    </View>
  );
}

export default function AreaScreen({ summary, onBack }: { summary: Summary; onBack: () => void }) {
  const max = Math.max(1, ...summary.by_time);
  return (
    <View style={{ flex: 1, backgroundColor: C.card }}>
      <ScrollView contentContainerStyle={s.pad}>
        <Pressable onPress={onBack} style={s.back}><Text style={s.backText}>‹ Harita</Text></Pressable>
        <Text style={s.label}>{summary.district.toUpperCase()}</Text>
        <Text style={s.title}>{summary.name}</Text>
        {summary.sample_data && <Text style={s.tag}>ÖRNEK VERİ</Text>}
        <View style={s.why}>
          <Text style={s.whyText}><Text style={{ fontWeight: '700' }}>Ne yapmalıyım? </Text>{adviceTr(summary.level)}{'\n\n'}Bu değerlendirme geçmiş olaylara dayanan bir tahmindir, kesin hüküm değildir.</Text>
        </View>
        <Text style={s.label}>OLAYLAR HANGİ SAATLERDE? (turuncu: olay bildirilen saatler)</Text>
        <View style={s.bars}>
          {summary.by_time.map((n, i) => (
            <Bar key={i} pct={Math.max(12, (n / max) * 100)} on={n > 0} delay={i * 70} />
          ))}
        </View>
        <View style={{ flexDirection: 'row', gap: 8 }}>
          {LABELS.map((l) => <Text key={l} style={s.hour}>{l}</Text>)}
        </View>
        <Text style={[s.label, { marginTop: 8 }]}>SON OLAYLAR · KAYNAĞIYLA</Text>
        {summary.events.map((e, i) => (
          <View key={i} style={s.ev}>
            <Text style={s.evTitle}>{KIND_TR[e.kind] ?? 'Olay bildirimi'}</Text>
            <Text style={s.evSub}>{e.source} · {agoTr(e.occurred_at)} · Güven: {confidenceTr(e.confidence)}</Text>
          </View>
        ))}
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <Pressable style={[s.btn, { backgroundColor: C.ink }]} onPress={() => Alert.alert('Yakında', 'Oylama sonraki sürümde.')}>
            <Text style={[s.btnText, { color: C.bg }]}>Burası sakin</Text>
          </Pressable>
          <Pressable style={[s.btn, { borderWidth: 1.5, borderColor: C.ink }]} onPress={() => Alert.alert('Yakında', 'Oylama sonraki sürümde.')}>
            <Text style={s.btnText}>Dikkat edilmeli</Text>
          </Pressable>
        </View>
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  pad: { padding: 24, paddingTop: 52, gap: 14 },
  back: { minHeight: 44, justifyContent: 'center' },
  backText: { fontSize: 16, fontWeight: '600', color: C.ink },
  label: { fontSize: 12, fontWeight: '600', letterSpacing: 0.6, color: C.sub },
  title: { fontSize: 30, fontWeight: '700', color: C.ink },
  tag: { alignSelf: 'flex-start', fontSize: 11, fontWeight: '600', color: C.sub, backgroundColor: '#F1E9D8', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 10, overflow: 'hidden' },
  why: { padding: 16, borderRadius: 20, backgroundColor: C.coralSoft },
  whyText: { fontSize: 16, lineHeight: 24, color: C.coralText },
  bars: { flexDirection: 'row', gap: 8, height: 64 },
  hour: { flex: 1, textAlign: 'center', fontSize: 11, color: C.sub },
  ev: { padding: 14, borderRadius: 16, borderWidth: 1, borderColor: '#E9E0CD' },
  evTitle: { fontSize: 14, fontWeight: '600', color: C.ink },
  evSub: { fontSize: 12, color: C.sub, marginTop: 2 },
  btn: { flex: 1, minHeight: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center' },
  btnText: { fontSize: 15, fontWeight: '600', color: C.ink },
});
