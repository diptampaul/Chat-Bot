import 'package:flutter/material.dart';

import 'assests/global.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'FinnOne Demo',
      scaffoldMessengerKey: snackbarKey,
      home: const Text("Home"),
      // initialRoute: '/',
      // routes: {
      //   '/' : (context) => const HomeScreen(),
      // },
    );
  }
}

