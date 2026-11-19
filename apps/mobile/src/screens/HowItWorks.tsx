import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { C } from '../theme';

const LEVELS = [
  ['#2E9E8A', 'Sakin', 'Son zamanlarda dikkat çeken olay yok.'],
  ['#E8A317', 'Hafif tedbirli', 'Bazı saatlerde dikkatli olmak iyi olur.'],
  ['#F07B3F', 'Tedbirli', 'Özellikle geceleri dikkat gerekir.'],
  ['#E5484D', 'Dikkatli ol', 'Yakın zamanda çok sayıda olay bildirildi.'],
];

export default function HowItWorks() {
  return (
    <ScrollView style={{ flex: 1, backgroundColor: C.bg }} contentContainerStyle={s.pad}>
      <Text style={s.h1}>Nasıl çalışır?</Text>
      <Text style={s.p}>Uygulama, haberlerden ve topluluk bildirimlerinden olayları toplar ve bir bölgenin hangi saatlerde nasıl olduğunu özetler.</Text>

      <Text style={s.h2}>Renkler ne anlama geliyor?</Text>
      {LEVELS.map(([color, name, desc]) => (
        <View key={name} style={s.row}>
          <View style={[s.dot, { backgroundColor: color }]} />
          <View style={{ flex: 1 }}><Text style={s.name}>{name}</Text><Text style={s.p}>{desc}</Text></View>
        </View>
      ))}

      <Text style={s.h2}>Bilgiler nereden geliyor?</Text>
      <Text style={s.p}>Haber siteleri, resmi açıklamalar ve topluluk bildirimleri. Her olayın yanında kaynağı ve ne kadar güvenilir olduğu yazar.</Text>

      <Text style={s.h2}>Önemli not</Text>
      <View style={s.note}>
        <Text style={s.noteText}>Değerlendirmeler geçmiş olaylara dayanan tahminlerdir, kesin hüküm değildir. Acil bir durumda <Text style={{ fontWeight: '700' }}>112</Text>'yi ara.</Text>
      </View>

      <Text style={s.h2}>Gizlilik</Text>
      <Text style={s.p}>Kişileri değil, olayları ve yerleri gösteririz. Konumun cihazında kalır.</Text>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  pad: { padding: 24, paddingTop: 56, gap: 12 },
  h1: { fontSize: 32, fontWeight: '700', color: C.ink },
  h2: { fontSize: 20, fontWeight: '700', color: C.ink, marginTop: 12 },
  p: { fontSize: 16, lineHeight: 24, color: C.body },
  row: { flexDirection: 'row', gap: 14, alignItems: 'flex-start', backgroundColor: C.card, borderRadius: 16, padding: 14, borderWidth: 1, borderColor: C.line },
  dot: { width: 22, height: 22, borderRadius: 11, marginTop: 2 },
  name: { fontSize: 16, fontWeight: '700', color: C.ink },
  note: { backgroundColor: C.coralSoft, borderRadius: 16, padding: 16 },
  noteText: { fontSize: 16, lineHeight: 24, color: C.coralText },
});
