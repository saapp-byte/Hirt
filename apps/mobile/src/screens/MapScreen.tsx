import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Animated, Easing, Pressable, StyleSheet, Text, View } from 'react-native';
import MapArt from '../MapArt';
import { Summary, adviceTr, levelColor, levelSegments, updatedTr } from '../api';
import { C } from '../theme';
import { FadeIn, PressScale } from '../ui';
import PlacePicker from './PlacePicker';
import { findMyPlace } from '../location';

type Props = { summary: Summary | null; updated?: string | null; onPick: (id: number) => void; onOpen: () => void; hintOpen: boolean; onCloseHint: () => void };

export default function MapScreen({ summary, updated, onPick, onOpen, hintOpen, onCloseHint }: Props) {
  const [pickerOpen, setPickerOpen] = useState(false);
  const [locBusy, setLocBusy] = useState(false);
  const [locNote, setLocNote] = useState<string | null>(null);
  const locate = async () => {
    setLocBusy(true); setLocNote(null);
    const r = await findMyPlace();
    setLocBusy(false);
    if ('error' in r) return setLocNote(r.error);
    setLocNote(`Konumuna en yakın bölge: ${r.name} (yaklaşık, ${r.km} km)`);
    onPick(r.id);
  };
  const slide = useRef(new Animated.Value(320)).current;
  useEffect(() => {
    Animated.timing(slide, { toValue: 0, duration: 520, delay: 150, easing: Easing.out(Easing.cubic), useNativeDriver: true }).start();
  }, []);
  const color = summary ? levelColor(summary.level) : C.ink;
  const segs = summary ? levelSegments(summary.level) : 0;
  return (
    <View style={{ flex: 1, backgroundColor: C.bg }}>
      <MapArt color={summary ? levelColor(summary.level) : undefined} />
      <View style={s.top}>
        <Pressable style={s.search} onPress={() => setPickerOpen(true)} accessibilityLabel="Yer ara">
          <Text style={s.searchText}>Yer ara: il, ilçe, mahalle</Text>
        </Pressable>
        <Pressable style={s.locBtn} onPress={locate} disabled={locBusy} accessibilityLabel="Bulunduğum yeri bul">
          <Text style={s.locText}>{locBusy ? 'Konum aranıyor…' : 'Bulunduğum yeri bul'}</Text>
        </Pressable>
        {!!locNote && <Text style={s.locNote}>{locNote}</Text>}
        {hintOpen && (
          <FadeIn style={s.hint} delay={700}>
            <Text style={s.hintText}>Yukarıdan bir il, ilçe veya mahalle seç. Kart, son 30 günde haberlerde geçen olayları özetler. Arkadaki harita sadece süstür.</Text>
            <PressScale onPress={onCloseHint} style={s.hintBtn}><Text style={s.hintBtnText}>Anladım</Text></PressScale>
          </FadeIn>
        )}
      </View>

      <Animated.View style={[s.sheet, { transform: [{ translateY: slide }] }]}>
        <View style={s.handle} />
        {!summary ? <ActivityIndicator color={C.ink} style={{ margin: 40 }} /> : (
          <>
            <Pressable onPress={() => setPickerOpen(true)} accessibilityLabel="Yer değiştir" style={s.placeRow}>
              <Text style={s.place}>{summary.place_level === 'il' ? summary.name : `${summary.name}, ${summary.district}`}</Text>
              <Text style={s.change}>Yer değiştir ›</Text>
            </Pressable>
            <View style={[s.pill, { backgroundColor: color }]}>
              <Text style={s.pillText}>{summary.level === 'Kayıt yok' ? summary.level : `Son 30 gün: ${summary.level}`}</Text>
            </View>
            <View style={{ flexDirection: 'row', gap: 6 }}>
              {[1, 2, 3, 4, 5].map((i) => <FadeIn key={i} rise={0} delay={500 + i * 90} style={{ flex: 1 }}><View style={[s.seg, i <= segs && { backgroundColor: color }]} /></FadeIn>)}
            </View>
            <Text style={s.body}>{adviceTr(summary.level)}</Text>
            {summary.sample_data && <Text style={s.tag}>ÖRNEK VERİ</Text>}
            {!!updated && <Text style={s.upd}>Veri güncellendi: {updatedTr(updated)}</Text>}
            <PressScale style={s.btn} onPress={onOpen}><Text style={s.btnText}>Nedenini ve detayları gör</Text></PressScale>
          </>
        )}
      </Animated.View>
      <PlacePicker visible={pickerOpen} onClose={() => setPickerOpen(false)} onPick={onPick} />
    </View>
  );
}

const s = StyleSheet.create({
  top: { position: 'absolute', top: 48, left: 16, right: 16, gap: 10 },
  search: { height: 54, borderRadius: 27, backgroundColor: C.card, borderWidth: 1, borderColor: C.line, paddingHorizontal: 20, justifyContent: 'center', elevation: 4 },
  locBtn: { alignSelf: 'flex-start', minHeight: 44, paddingHorizontal: 18, borderRadius: 22, backgroundColor: C.ink, justifyContent: 'center' },
  locText: { color: C.bg, fontSize: 15, fontWeight: '600' },
  locNote: { fontSize: 13, color: C.ink, backgroundColor: C.card, borderRadius: 12, padding: 10, overflow: 'hidden' },
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
  upd: { fontSize: 12, color: C.sub },
  place: { fontSize: 24, fontWeight: '700', color: C.ink },
  pill: { alignSelf: 'flex-start', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 18 },
  pillText: { color: '#FFFFFF', fontSize: 15, fontWeight: '700' },
  seg: { flex: 1, height: 8, borderRadius: 4, backgroundColor: C.track },
  body: { fontSize: 16, lineHeight: 24, color: C.body },
  tag: { alignSelf: 'flex-start', fontSize: 11, fontWeight: '600', color: C.sub, backgroundColor: '#F1E9D8', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 10, overflow: 'hidden' },
  btn: { minHeight: 54, borderRadius: 27, backgroundColor: C.ink, alignItems: 'center', justifyContent: 'center', marginTop: 4 },
  btnText: { color: C.bg, fontSize: 16, fontWeight: '600' },
  placeRow: { gap: 2, minHeight: 44, justifyContent: 'center' },
  change: { fontSize: 14, fontWeight: '600', color: C.sub },
  modalBg: { flex: 1, backgroundColor: 'rgba(29,27,46,0.45)', justifyContent: 'flex-end' },
  modalCard: { maxHeight: '80%', backgroundColor: C.card, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 20, gap: 12 },
  modalTitle: { fontSize: 22, fontWeight: '700', color: C.ink },
  row: { flexDirection: 'row', alignItems: 'center', gap: 14, minHeight: 56, borderBottomWidth: 1, borderBottomColor: '#EFE7D6' },
  dot: { width: 14, height: 14, borderRadius: 7 },
  rowName: { fontSize: 17, fontWeight: '600', color: C.ink },
  rowSub: { fontSize: 14, color: C.sub },
});
