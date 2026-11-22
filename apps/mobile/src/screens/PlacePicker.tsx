import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { Area, fetchAreas, levelColor } from '../api';
import { C } from '../theme';
import { PressScale } from '../ui';

type Crumb = { id: number; name: string };
type Props = { visible: boolean; onClose: () => void; onPick: (id: number) => void };

// Türkçe büyük/küçük harf ve aksan farkını yok sayan basit arama
const fold = (t: string) =>
  t.toLocaleLowerCase('tr').replace(/ı/g, 'i').replace(/ş/g, 's').replace(/ğ/g, 'g').replace(/ü/g, 'u').replace(/ö/g, 'o').replace(/ç/g, 'c');

// İl -> ilçe -> (olay olan) mahalle gezintisi. Hangi seviyede seçilirse o bölgenin özeti açılır.
export default function PlacePicker({ visible, onClose, onPick }: Props) {
  const [trail, setTrail] = useState<Crumb[]>([]);
  const [list, setList] = useState<Area[]>([]);
  const [loading, setLoading] = useState(false);
  const [q, setQ] = useState('');

  const parent = trail.length ? trail[trail.length - 1] : null;

  useEffect(() => {
    if (!visible) return;
    let alive = true;
    setLoading(true);
    setQ('');
    fetchAreas(parent?.id).then((r) => {
      if (!alive) return;
      setList(r);
      setLoading(false);
    });
    return () => { alive = false; };
  }, [visible, parent?.id]);

  const shown = useMemo(() => (q.trim() ? list.filter((a) => fold(a.name).includes(fold(q.trim()))) : list), [list, q]);

  const pick = (id: number) => { onPick(id); setTrail([]); onClose(); };
  const open = async (a: Area) => {
    // Alt bölge varsa içine gir, yoksa doğrudan seç
    const kids = await fetchAreas(a.id);
    if (kids.length === 0 || trail.length >= 2) return pick(a.id);
    setTrail([...trail, { id: a.id, name: a.name }]);
  };
  const close = () => { setTrail([]); onClose(); };
  const title = parent ? parent.name : 'İl seç';
  const hint = trail.length === 0 ? 'Bir il seç' : trail.length === 1 ? 'İlçe seç' : 'Olay bildirilen mahalleler';

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={close}>
      <View style={s.bg}>
        <View style={s.card}>
          <View style={s.head}>
            {parent ? (
              <Pressable style={s.backBtn} onPress={() => setTrail(trail.slice(0, -1))} accessibilityLabel="Geri">
                <Text style={s.backText}>‹ Geri</Text>
              </Pressable>
            ) : <View style={s.backBtn} />}
            <Pressable style={s.backBtn} onPress={close} accessibilityLabel="Kapat"><Text style={s.backText}>Kapat</Text></Pressable>
          </View>
          <Text style={s.title}>{title}</Text>
          <Text style={s.hint}>{hint}</Text>
          <TextInput
            value={q} onChangeText={setQ} placeholder="Ara…" placeholderTextColor={C.sub}
            style={s.input} autoCorrect={false} autoCapitalize="none"
          />
          {loading ? <ActivityIndicator color={C.ink} style={{ margin: 30 }} /> : (
            <ScrollView keyboardShouldPersistTaps="handled">
              {parent && (
                <Pressable style={s.row} onPress={() => pick(parent.id)}>
                  <View style={[s.dot, { backgroundColor: C.ink }]} />
                  <View style={{ flex: 1 }}>
                    <Text style={s.rowName}>Tümü: {parent.name}</Text>
                    <Text style={s.rowSub}>Bölgenin geneli</Text>
                  </View>
                </Pressable>
              )}
              {shown.length === 0 && <Text style={s.empty}>{q ? 'Eşleşen yer yok.' : 'Liste alınamadı. İnternet bağlantını kontrol et.'}</Text>}
              {shown.map((a) => (
                <Pressable key={a.id} style={s.row} onPress={() => open(a)}>
                  <View style={[s.dot, { backgroundColor: levelColor(a.level) }]} />
                  <View style={{ flex: 1 }}>
                    <Text style={s.rowName}>{a.name}</Text>
                    <Text style={s.rowSub}>{a.count > 0 ? `${a.count} olay · ${a.level}` : 'Kayıt yok'}</Text>
                  </View>
                  <Text style={s.chev}>›</Text>
                </Pressable>
              ))}
            </ScrollView>
          )}
          <PressScale style={s.btn} onPress={close}><Text style={s.btnText}>Vazgeç</Text></PressScale>
        </View>
      </View>
    </Modal>
  );
}

const s = StyleSheet.create({
  bg: { flex: 1, backgroundColor: 'rgba(29,27,46,0.45)', justifyContent: 'flex-end' },
  card: { maxHeight: '88%', backgroundColor: C.card, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 20, gap: 8 },
  head: { flexDirection: 'row', justifyContent: 'space-between' },
  backBtn: { minHeight: 44, minWidth: 64, justifyContent: 'center' },
  backText: { fontSize: 16, fontWeight: '600', color: C.ink },
  title: { fontSize: 24, fontWeight: '700', color: C.ink },
  hint: { fontSize: 13, color: C.sub },
  input: { height: 48, borderRadius: 24, borderWidth: 1, borderColor: C.line, paddingHorizontal: 18, fontSize: 16, color: C.ink, backgroundColor: C.bg },
  row: { flexDirection: 'row', alignItems: 'center', gap: 14, minHeight: 58, borderBottomWidth: 1, borderBottomColor: '#EFE7D6' },
  dot: { width: 14, height: 14, borderRadius: 7 },
  rowName: { fontSize: 17, fontWeight: '600', color: C.ink },
  rowSub: { fontSize: 14, color: C.sub },
  chev: { fontSize: 22, color: C.sub },
  empty: { fontSize: 15, color: C.sub, padding: 16 },
  btn: { minHeight: 52, borderRadius: 26, backgroundColor: C.ink, alignItems: 'center', justifyContent: 'center', marginTop: 4 },
  btnText: { color: C.bg, fontSize: 16, fontWeight: '600' },
});
