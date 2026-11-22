import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { C } from '../theme';

const LEVELS = [
  ['#2E9E8A', 'Sakin', 'Son 30 günde dikkat çeken olay görünmüyor.'],
  ['#E8A317', 'Hafif tedbirli', 'Son 30 günde birkaç olay bildirildi.'],
  ['#F07B3F', 'Tedbirli', 'Son 30 günde olay sayısı belirgin.'],
  ['#E5484D', 'Dikkatli ol', 'Son 30 günde çok sayıda olay bildirildi.'],
  ['#8A8599', 'Kayıt yok', 'Tarama sonucunda bulunamadı. Güvenli demek değildir.'],
];

export default function HowItWorks() {
  return (
    <ScrollView style={{ flex: 1, backgroundColor: C.bg }} contentContainerStyle={s.pad}>
      <Text style={s.h1}>Nasıl çalışır?</Text>
      <Text style={s.p}>Uygulama, Türkiye’deki haber sitelerini düzenli tarar; kavga, saldırı ve bıçaklama haberlerini bulur ve bölge bölge özetler.</Text>

      <Text style={s.h2}>Renkler ne anlama geliyor?</Text>
      {LEVELS.map(([color, name, desc]) => (
        <View key={name} style={s.row}>
          <View style={[s.dot, { backgroundColor: color }]} />
          <View style={{ flex: 1 }}><Text style={s.name}>{name}</Text><Text style={s.p}>{desc}</Text></View>
        </View>
      ))}

      <Text style={s.h2}>Bilgiler nereden geliyor?</Text>
      <Text style={s.p}>Yalnızca haber siteleri ve haber arama sonuçları. Her olayın yanında kaynağı, haberin bağlantısı ve güven düzeyi yazar. Olaylar başlıklardan otomatik çıkarıldığı için hata olabilir.</Text>

      <Text style={s.h2}>"Kayıt yok" ne demek?</Text>
      <Text style={s.p}>Gri etiket, tarama sonucunda o bölge için haber bulunamadığını gösterir. Uygulama her haberi yakalayamaz; başlığında ilçe adı geçmeyen haberler atlanır. Bu yüzden "Kayıt yok", güvenli demek değildir.</Text>

      <Text style={s.h2}>Önemli not</Text>
      <View style={s.note}>
        <Text style={s.noteText}>Değerlendirmeler geçmiş olaylara dayanan tahminlerdir, kesin hüküm değildir. Acil bir durumda <Text style={{ fontWeight: '700' }}>112</Text>'yi ara.</Text>
      </View>

      <Text style={s.h2}>Gizlilik</Text>
      <Text style={s.p}>Kişileri değil, olayları ve yerleri gösteririz. Uygulama konumunu istemez ve kişisel veri toplamaz.</Text>
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
