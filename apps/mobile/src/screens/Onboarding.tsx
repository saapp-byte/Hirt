import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Svg, { Circle, Path } from 'react-native-svg';
import { C } from '../theme';
import { FadeIn, PressScale, PulseRings } from '../ui';

const LEVELS = [
  ['#2E9E8A', 'Sakin', 'Son 30 günde dikkat çeken olay görünmüyor.'],
  ['#E8A317', 'Tedbirli', 'Son 30 günde olay sayısı belirgin.'],
  ['#E5484D', 'Dikkatli ol', 'Son 30 günde çok sayıda olay bildirildi.'],
];

export default function Onboarding({ onStart }: { onStart: () => void }) {
  const [i, setI] = useState(0);
  const last = i === 2;
  return (
    <View style={s.root}>
      <View style={s.skipRow}>
        {!last ? <Pressable onPress={onStart} style={s.skip}><Text style={s.skipText}>Atla</Text></Pressable> : null}
      </View>

      <FadeIn key={i} rise={12} style={{ flex: 1 }}>
      {i === 0 && (
        <View style={s.body}>
          <View style={{ alignSelf: 'center', width: 230, height: 230, alignItems: 'center', justifyContent: 'center' }}>
          <PulseRings size={230} />
          <Svg width={230} height={230} viewBox="0 0 334 330">
            <Circle cx="167" cy="165" r="150" fill="#FFE4DA" />
            <Circle cx="167" cy="165" r="105" fill="#FFCDBB" />
            <Circle cx="167" cy="165" r="58" fill="#F07B3F" fillOpacity="0.85" />
            <Path d="M20 120 L320 210 M110 20 L230 310" stroke="#FFFDF8" strokeWidth="10" strokeLinecap="round" fill="none" />
            <Circle cx="167" cy="165" r="20" fill="#1D1B2E" />
            <Circle cx="167" cy="165" r="7" fill="#F6F1E7" />
          </Svg>
          </View>
          <Text style={s.title}>Gideceğin yerin nasıl olduğunu önceden gör</Text>
          <Text style={s.text}>Haberlerde bildirilen olaylara dayanarak, bir bölgede son zamanlarda neler olduğunu tek bakışta gör.</Text>
        </View>
      )}

      {i === 1 && (
        <View style={s.body}>
          <Text style={s.title}>Renkler ne anlama geliyor?</Text>
          <Text style={s.text}>Haritada ve kartlarda üç seviye göreceksin:</Text>
          {LEVELS.map(([color, name, desc]) => (
            <View key={name} style={s.level}>
              <View style={[s.swatch, { backgroundColor: color }]} />
              <View style={{ flex: 1 }}>
                <Text style={s.levelName}>{name}</Text>
                <Text style={s.levelDesc}>{desc}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {i === 2 && (
        <View style={s.body}>
          <Text style={s.title}>Önce güvenin ve mahremiyetin</Text>
          {[
            ['Kişileri değil, olayları gösteririz', 'Hiçbir kişi veya grup etiketlenmez.'],
            ['Her bilginin kaynağı yanında', 'Olayın hangi haberden geldiğini görür, haberi açıp okuyabilirsin.'],
            ['Konumunu istemeyiz', 'Uygulama kişisel veri toplamaz.'],
          ].map(([t, d]) => (
            <View key={t} style={s.level}>
              <View style={[s.swatch, { backgroundColor: C.teal, width: 12, height: 12, borderRadius: 6, marginTop: 6 }]} />
              <View style={{ flex: 1 }}>
                <Text style={s.levelName}>{t}</Text>
                <Text style={s.levelDesc}>{d}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      </FadeIn>
      <View style={s.dots}>
        {[0, 1, 2].map((n) => <View key={n} style={[s.pip, n === i && s.pipOn]} />)}
      </View>
      <PressScale style={s.btn} onPress={() => (last ? onStart() : setI(i + 1))}>
        <Text style={s.btnText}>{last ? 'Haritayı aç' : 'Devam'}</Text>
      </PressScale>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg, paddingHorizontal: 28, paddingBottom: 32 },
  skipRow: { height: 92, alignItems: 'flex-end', justifyContent: 'flex-end' },
  skip: { minHeight: 44, minWidth: 44, justifyContent: 'center', alignItems: 'center' },
  skipText: { fontSize: 16, color: C.sub, fontWeight: '600' },
  body: { flex: 1, gap: 14 },
  title: { fontSize: 30, fontWeight: '700', color: C.ink, lineHeight: 36 },
  text: { fontSize: 17, lineHeight: 25, color: C.body },
  level: { flexDirection: 'row', gap: 14, alignItems: 'flex-start', backgroundColor: C.card, borderRadius: 18, padding: 16, borderWidth: 1, borderColor: C.line },
  swatch: { width: 22, height: 22, borderRadius: 11, marginTop: 2 },
  levelName: { fontSize: 17, fontWeight: '700', color: C.ink },
  levelDesc: { fontSize: 15, lineHeight: 22, color: C.body, marginTop: 2 },
  dots: { flexDirection: 'row', gap: 8, justifyContent: 'center', marginBottom: 18 },
  pip: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#DDD2BC' },
  pipOn: { width: 24, backgroundColor: C.ink },
  btn: { minHeight: 56, borderRadius: 28, backgroundColor: C.ink, alignItems: 'center', justifyContent: 'center' },
  btnText: { color: C.bg, fontSize: 17, fontWeight: '600' },
});
