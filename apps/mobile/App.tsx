import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { Summary, fetchAreas, fetchSummary, fetchUpdated } from './src/api';
import { C } from './src/theme';
import { FadeIn } from './src/ui';
import AreaScreen from './src/screens/AreaScreen';
import HowItWorks from './src/screens/HowItWorks';
import MapScreen from './src/screens/MapScreen';
import Onboarding from './src/screens/Onboarding';

type Screen = 'onboard' | 'map' | 'area' | 'info';

export default function App() {
  const [screen, setScreen] = useState<Screen>('onboard');
  const [summary, setSummary] = useState<Summary | null>(null);
  const [hintOpen, setHintOpen] = useState(true);

  const [areaId, setAreaId] = useState<number | null>(null);
  const [updated, setUpdated] = useState<string | null>(null);

  // Açılışta İstanbul (plaka 34) açılır; il listesi alınamazsa yine de 34 denenir
  useEffect(() => {
    fetchUpdated().then(setUpdated);
    fetchAreas().then((a) => setAreaId(a.some((x) => x.id === 34) ? 34 : a.length ? a[0].id : 34));
  }, []);

  useEffect(() => {
    if (areaId === null) return;
    setSummary(null);
    fetchSummary(areaId).then((r) => setSummary(r.data));
  }, [areaId]);

  const showTabs = screen === 'map' || screen === 'info';
  const Tab = ({ id, label }: { id: Screen; label: string }) => (
    <Pressable onPress={() => setScreen(id)} style={{ flex: 1, minHeight: 56, alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: 15, fontWeight: screen === id ? '700' : '500', color: screen === id ? C.ink : C.sub }}>{label}</Text>
      <View style={{ height: 3, width: 28, borderRadius: 2, marginTop: 4, backgroundColor: screen === id ? C.coral : 'transparent' }} />
    </Pressable>
  );

  return (
    <View style={{ flex: 1, backgroundColor: C.bg }}>
      <StatusBar style="dark" />
      <FadeIn key={screen} rise={10} style={{ flex: 1 }}>
        {screen === 'onboard' && <Onboarding onStart={() => setScreen('map')} />}
        {screen === 'map' && <MapScreen summary={summary} updated={updated} onPick={setAreaId} onOpen={() => setScreen('area')} hintOpen={hintOpen} onCloseHint={() => setHintOpen(false)} />}
        {screen === 'area' && summary && <AreaScreen summary={summary} onBack={() => setScreen('map')} />}
        {screen === 'info' && <HowItWorks />}
      </FadeIn>
      {showTabs && (
        <View style={{ flexDirection: 'row', backgroundColor: C.card, borderTopWidth: 1, borderTopColor: C.line, paddingBottom: 8 }}>
          <Tab id="map" label="Harita" />
          <Tab id="info" label="Nasıl çalışır?" />
        </View>
      )}
    </View>
  );
}
